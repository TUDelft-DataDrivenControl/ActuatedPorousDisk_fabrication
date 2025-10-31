from playsound import playsound
import pyautogui

def start_wind():
    pyautogui.press('playpause')
    playsound('./StartAudio.mp3')
    pyautogui.press('playpause')

def stop_wind():
    pyautogui.press('playpause')
    playsound('./StopAudio.mp3')
    pyautogui.press('playpause')
