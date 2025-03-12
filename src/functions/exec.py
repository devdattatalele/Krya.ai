import os
import time
import pyautogui

def run_script():
    try:
        # Use Command + Space to open Spotlight
        pyautogui.hotkey('command', 'space')
        time.sleep(1)
        pyautogui.typewrite('terminal', interval=0.1)
        pyautogui.press('enter')
        time.sleep(2)
        # Open new terminal tab
        pyautogui.hotkey('command', 't')
        time.sleep(2)
        # Run the script
        script_path = os.path.join(os.getcwd(), "src", "generated_output", "generated_output.py")
        pyautogui.typewrite(f'python3 "{script_path}"\n', interval=0.01)

        return "Script execution initiated. Check the terminal for results."

    except Exception as e:
        return f"An error occurred: {e}"
