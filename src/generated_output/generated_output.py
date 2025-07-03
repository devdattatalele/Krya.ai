import pyautogui
import time

try:
    # Open Spotlight
    pyautogui.keyDown('command')
    pyautogui.press('space')
    pyautogui.keyUp('command')
    time.sleep(1)

    # Type "TextEdit" and press Enter to open the application
    pyautogui.write('TextEdit', interval=0.1)
    pyautogui.press('enter')
    time.sleep(2)  # Give TextEdit time to open

    # Check if a new document is already open or create a new one (Command + N)
    # This might depend on TextEdit's last state, so opening a new one is safer
    pyautogui.keyDown('command')
    pyautogui.press('n')
    pyautogui.keyUp('command')
    time.sleep(1) # Give time for the new document window to appear

    # Type the desired text
    pyautogui.write('y0oooihTextEdit', interval=0.01)

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure PyAutoGUI is installed and accessibility permissions are granted for your terminal/IDE.")
    print("Also, make sure TextEdit is installed on your system.")