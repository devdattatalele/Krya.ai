import pyautogui
import time

try:
    # Open Spotlight
    pyautogui.keyDown('command')
    pyautogui.press('space')
    pyautogui.keyUp('command')
    time.sleep(2) # Give Spotlight time to appear

    # Type "TextEdit" and press Enter to open the application
    pyautogui.write('TextEdit')
    time.sleep(0.5) # Give some time for the text to appear in Spotlight
    pyautogui.press('enter')
    time.sleep(3) # Give TextEdit time to open

    # Open a new document (Command + N)
    pyautogui.keyDown('command')
    pyautogui.press('n')
    pyautogui.keyUp('command')
    time.sleep(1) # Give time for the new window to appear

except Exception as e:
    # Basic error handling
    print(f"An error occurred: {e}")
    print("Please ensure PyAutoGUI has accessibility permissions in System Settings > Privacy & Security > Accessibility.")
    print("Also, check if 'TextEdit' is correctly installed and accessible via Spotlight.")