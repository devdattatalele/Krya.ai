import pyautogui
import time
import pyperclip

try:
    # Open Chrome
    pyautogui.hotkey('command', 'space')
    time.sleep(2)
    pyautogui.write('Chrome')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(5)
    pyautogui.hotkey('command', 't')
    time.sleep(2)

    # Define websites and search term
    websites = {
        "Amazon": "https://www.amazon.in/s?k=phones+under+20000",
        "Flipkart": "https://www.flipkart.com/search?q=phones+under+20000&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off",
    }
    search_term = "phones under 20000"


    for website_name, url in websites.items():
        pyperclip.copy(url)
        pyautogui.hotkey('command', 'v')
        pyautogui.press('enter')
        time.sleep(5)

        # Scroll down for more results (adjust scroll amount as needed)
        pyautogui.scroll(-500)  # Scroll dow
        time.sleep(3)




except Exception as e:
    print(f"An error occurred: {e}")
