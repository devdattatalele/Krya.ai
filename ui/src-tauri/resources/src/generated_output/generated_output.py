import pyautogui
import time

try:
    # Open Spotlight
    pyautogui.keyDown('command')
    pyautogui.press('space')
    pyautogui.keyUp('command')
    time.sleep(1)

    # Type 'TextEdit' to search for the application
    pyautogui.write('TextEdit', interval=0.01)
    time.sleep(0.5)

    # Press Enter to open TextEdit
    pyautogui.press('enter')
    time.sleep(2)  # Give TextEdit time to open

    # Ensure a new document is open (TextEdit usually opens a new one by default, but this ensures it)
    pyautogui.keyDown('command')
    pyautogui.press('n')
    pyautogui.keyUp('command')
    time.sleep(1) # Give time for new document to appear

    # Type the specified text
    pyautogui.write('harshenj;ksgkna', interval=0.01)
    time.sleep(0.5)

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure TextEdit is installed and accessible.")
    print("Also, check PyAutoGUI's accessibility permissions in macOS System Settings > Security & Privacy > Accessibility.")