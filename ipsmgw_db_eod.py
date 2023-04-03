# /root/ipsmgw/db_eod/db_eod.sql
import os

file_name = '/root/ipsmgw/db_eod/db_eod.sql'

old_text = ""
new_text = ""

# print(os.system("ls -al"))

print(os.system("grep SYSDATE /root/ipsmgw/db_eod/db_eod.sql"))



