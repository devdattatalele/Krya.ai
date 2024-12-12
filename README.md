

<h1 align="center">Krya.ai: LLM Automation System</h1>

<p align="center">



</p>

<br>



### Overview
Krya.ai is an innovative orchestration system that empowers you to automate complex tasks on your local machine using the power of Large Language Models (LLMs) like Google Gemini. This initial release focuses on streamlining workflows by generating and executing code, with a sophisticated feedback loop that refines code through error handling and continuous learning.  Think of Krya.ai as your intelligent, automated assistant capable of understanding and executing your instructions directly on your computer.
<br>


 ### What Can Krya.ai Do?

*   **Automated Code Execution:** Krya.ai generates code based on your instructions and executes it in your local environment.
*   **Intelligent Task Automation:** It automates cursor movements, clicks, and typing, enabling you to interact with your desktop applications programmatically.
*  **Error Handling & Refinement:** A feedback loop allows Krya.ai to learn from errors and refine its code, improving accuracy and efficiency over time.
*   **Extensible Architecture:** Built to be easily adaptable and extended for future integrations.
  
## Demo

[Screencast from 2024-12-12 19-30-55.webm](https://github.com/user-attachments/assets/16032e7a-69c1-4c42-b104-e8f13efa5b01)

[Screencast from 2024-12-12 19-27-37.webm](https://github.com/user-attachments/assets/11e7fe3b-e4fa-480c-a0f4-1c578e87dda3)

## Installations- 

### Prerequisites

-   Python 3.8 or higher
-   `pyautogui` library for UI automation
-   `google.generativeai` library for Gemini integration
-   `pyperclip` library for clipboard interaction
-   `streamlit` for the web interface
-   Access to Gemini API keys.

### Install Dependencies:

```bash
  pip install pyautogui google.generativeai pyperclip streamlit
```

### Setup API keys { for now we, are limited to GEMINI and LLAMA API (NIM API) }

#### Steps for GEMINI API

  1. GEMINI API = https://aistudio.google.com/app/apikey
  2. Login through your google account
  3. Create an API key
  4. Select your project
  5. Your api key will be create, it will look like : AIzaSxxxxxxxxxxh09xxLwCA
  6. Store it safe

### Clone the Krya.ai Repository:

```bash
  git clone https://github.com/devdattatalele/Krya.ai.git
  cd Krya.ai
```
### Running the Project

1.  Navigate to the directory where you cloned the repository.
2.  Launch the Streamlit app:

    ```bash
    streamlit run src/main.py
    ```
3.  Enter your saved API keys when prompted in the Streamlit app interface.
4.  Follow the interactive prompts and begin automating your tasks.

## Workflow

### Code Execution

1.  **LLM Code Generation:** Based on your instructions, Krya.ai generates code snippets.
2.  **Execution Environment:** The generated code is sent to your local machine's execution environment to run through a Python interpreter.
3.  **Output Feedback:** Results or errors from the code execution are sent back to the LLM, which allows for refining the code for improved performance if needed.

### Automated Cursor Movement and UI Interactions

1.  **PyAutoGUI Scripts:** The LLM generates scripts using PyAutoGUI for tasks like mouse movements, clicks, and keyboard inputs.
2.  **Script Execution:** The generated scripts are executed to automate the specified UI tasks.

    **Example Task:** Open a text editor and type "Hello, World!".

    ```python
    import pyautogui
    import time

    # Open the text editor (this may vary based on the system)
    pyautogui.hotkey('win')
    pyautogui.typewrite('notepad\n', interval=0.1)
    time.sleep(1)

    # Type "Hello, World!"
    pyautogui.typewrite('Hello, World!', interval=0.1)
    ```

    **Execution:** Running this Python script with PyAutoGUI installed will automate the process of opening Notepad and typing "Hello, World!".

## Use Cases

-   **Automated Testing:**  Generate and execute test scripts based on user instructions.
-   **GUI Automation:**  Automate repetitive tasks such as form filling, software navigation, and more.
-   **Task Automation:** Automate complex workflows that require both code and UI interactions.
-   **Personal Assistant:** Use it to automate your day-to-day computer tasks.

## Contributing

We welcome contributions! If you have any ideas for features or improvements, feel free to create pull requests.

## License

This project is licensed under the [Insert License Name Here] License.

## Future Enhancements

- Support for more LLMs (OpenAI, others).
- Improved error handling.
- Enhanced user interface.
- More complex automation workflows.
- Support for more operating systems.
