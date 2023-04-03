# https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
# click event code
import pyautogui
import win32api
import time

#pyautogui.mouseInfo()
print(pyautogui.size()) # 현재 모니터의 크기 파악

profile_x,profile_y = 1591,730 # 프로필 위치
btn_x, btn_y = 1255,587 # 공감버튼 위치
evt_close = 0 # 프로그램 진행 0, 끝내기 1

time.sleep(3) # 카카오톡 프로그램이 최상단에 위치하기 위한 시간
# print(pyautogui.position()) # 마우스의 현재 위치 표시
cnt=0   # while 문 동작 횟수 한번에 10회 클릭
#pyautogui.moveTo(profile_x,profile_y)   # 프로필 위치
time.sleep(1) # 위치 이동 후 sleep
#pyautogui.click()
time.sleep(1)

# 현재위치에서 자동클릭
while cnt<100:
    if win32api.GetKeyState(0x02) < 0: # 마우스 오른쪽 클릭하고있으면 멈춤
        print("count = {}".format(cnt))
        break
    pyautogui.moveTo(btn_x,btn_y)
    cnt+=1
    pyautogui.click(clicks=10, interval=0.0001) #클릭횟수, 클릭시간차
    time.sleep(0.1)
