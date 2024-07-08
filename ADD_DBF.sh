#!/bin/sh

# Set the data
# ORACLE : USER_PATH / SQLPLUS / ORACLE_SID / PASSWORD / TBS_NAME / HOST / PORT / SQLPLUS
# ALTIBASE : USER_PATH / iSQL / USERNAME / PASSWORD / TBS_NAME / HOST / PORT

USER_PATH="/inticube/smsom/pilot/supportkt"
OUTPUT_FILE="$USER_PATH/output.log"

ORACLE_DBF() {
    ORACLE_SID="HSMSCOM"
    USERNAME="smsom"
    PASSWORD="smsom"
    TBS_NAME="OM_DATA"
    HOST="localhost"
    PORT="1521"
    SQLPLUS="/home/oracle/db/product/12.1.0.2/dbhome_1/bin/sqlplus"
    
    ORA_CHECK=$($SQLPLUS $USERNAME/$PASSWORD@$ORACLE_SID << EOF
    EXIT;
EOF
    )
    if [[ $ORA_CHECK == *"Oracle"* ]]; then
        echo "Oracle DB running."
    else
        echo "Oracle DB not running"
        exit 1
    fi

    $SQLPLUS -s /nolog <<EOF > /dev/null
SPOOL $OUTPUT_FILE
CONNECT $USERNAME/$PASSWORD@$HOST:$PORT/$ORACLE_SID
SET TERMOUT OFF
SET FEEDBACK OFF
SET ECHO OFF
SET PAGESIZE 1000
SET LINESIZE 200
SET TRIMSPOOL ON 
col tablespace_name for a10 
col file_name for a50
SELECT tablespace_name, file_name, user_bytes/1024/1024 "U\sed(MB)", bytes/1024/1024 "total(MB)", maxbytes/1024/1024 "max(MB)", autoextensible "AUTO", online_status
FROM dba_data_files;
SPOOL OFF
EXIT;
EOF

    if [ $? -ne 0 ]; then
        echo "SQL*Plus Error"
        echo "CHECK OUTPUT FILE : $OUTPUT_FILE"
        echo "CHECK TBS_NAME : $TBS_NAME"
        exit 1
    fi

    echo "Success: Query executed successfully"
    echo "Logging results to $OUTPUT_FILE"

    current_file=$(\awk -v tbs_name="$TBS_NAME" '$1 == tbs_name {print $2}' $OUTPUT_FILE | \sort -k2,2n | \tail -1)

    if [ -z "$current_file" ]; then
        echo "Check the dbf file: $current_file"
        exit 1
    fi

    filename=$(basename "$current_file")
    index=$(echo "$filename" | \grep -o '[0-9]*' | \tail -1)

    if [ -z "$index" ]; then
        echo "Not Found Tablespace $TBS_NAME"
        exit 1
    fi

    next_index=$(printf "%02d" $((10#$index + 1)))

    new_filename=$(echo "$filename" | \sed "s/[0-9]*\./$next_index./")
    new_file_path=$(dirname "$current_file")/$new_filename

    echo -e "\n[Guide to adding dbf files]"
    echo "$ su - oracle"
    echo "$ sqlplus '/as sysdba'"
    echo "SQL> ALTER TABLESPACE $TBS_NAME ADD DATAFILE '$new_file_path' SIZE 1G AUTOEXTEND ON NEXT 100M MAXSIZE 31G;"
}

ALTIBASE_DBF() {
    iSQL="/altibase/altibase_home/bin/isql"
    USERNAME="smsom"
    PASSWORD="smsom"
    TBS_NAME="OM_DATA"
    HOST="localhost"
    PORT="20300"
    isql_cmd="$iSQL -s $HOST -u $USERNAME -p $PASSWORD -port $PORT"

    ISQL_OUTPUT=$($isql_cmd << EOF
    EXIT;
EOF
    )

    if [[ $ISQL_OUTPUT == *"Altibase"* ]]; then
        echo "Altibase DB running"
    else
        echo "Altibase DB not running"
        exit 1
    fi

    $isql_cmd <<EOF > /dev/null
set linesize 1024;
set colsize 30;
set feedback off;
SPOOL $OUTPUT_FILE
SELECT b.name tbs_name, a.id 'FILE#', a.name datafile_name,
             currsize*8/1024 'ALLOC(M)', round(case2(a.maxsize=0, currsize, a.maxsize)*8/1024) 'MAX(M)',
             decode(autoextend, 0, 'OFF', 'ON') 'AUTOEXTEND'
FROM v\$datafiles a, v\$tablespaces b WHERE b.id = a.spaceid
ORDER BY b.name, a.id;
SPOOL OFF
EXIT;
EOF

    if [ $? -ne 0 ]; then
        echo "ISQL_CONNECTION ERROR"
        echo "CHECK OUTPUT FILE : $OUTPUT_FILE"
        echo "CHECK TBS_NAME : $TBS_NAME"
        exit 1
    fi

    echo "Success: Query executed successfully"
    echo "Logging results to $OUTPUT_FILE"

    current_file=$(\awk -v tbs_name="$TBS_NAME" '$1 == tbs_name {print $3}' $OUTPUT_FILE | \sort -k2,2n | \tail -1)

    if [ -z "$current_file" ]; then
        echo "Check the dbf file : $current_file"
        exit 1
    fi

    filename=$(basename "$current_file")
    index=$(echo "$filename" | \grep -o '[0-9]*' | \tail -1)

    if [ -z "$index" ]; then
        echo "Not Found Tablespace $TBS_NAME"
        exit 1
    fi

    next_index=$(printf "%02d" $((10#$index + 1)))
    new_filename=$(echo "$filename" | \sed "s/[0-9]*\./$next_index./")
    new_file_path=$(dirname "$current_file")/$new_filename

    echo -e "\n[Guide to adding dbf files]"
    echo "$ su - altibase"
    echo "$ isql -s 127.0.0.1 -u sys -p manager"
    echo "iSQL> ALTER TABLESPACE $TBS_NAME ADD DATAFILE '$new_file_path' AUTOEXTEND ON NEXT 100M MAXSIZE 31G;"
}

CHECK_DBMS() {
    if ps -ef | \grep -q '[o]ra_pmon'; then
        echo "oracle"
        return
    fi

    if ps -ef | \grep -q '[a]ltibase'; then
        echo "altibase"
        return
    fi

    echo "unknown"
}

DBMS=$(CHECK_DBMS)

echo "=========================================="
echo "DB type : $DBMS"

if [ "$DBMS" = 'oracle' ]; then
    ORACLE_DBF
elif [ "$DBMS" = 'altibase' ]; then
    ALTIBASE_DBF
else
    echo "DB TYPE Error"
fi
echo "=========================================="
