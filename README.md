
# Krya.ai: LLM Orchestration and Automation System

### Overview
Krya.ai is an advanced orchestration system designed to enable automated interactions and code execution on local machine using powerful LLMs like OpenAI's GPT and Meta's LLaMA. In this initial release, Automatixc  focuses on automating workflows and executing code efficiently, with a feedback loop for error handling and refinement.

## Demo

[Screencast from 2024-12-12 19-30-55.webm](https://github.com/user-attachments/assets/16032e7a-69c1-4c42-b104-e8f13efa5b01)

[Screencast from 2024-12-12 19-27-37.webm](https://github.com/user-attachments/assets/11e7fe3b-e4fa-480c-a0f4-1c578e87dda3)

## Installation

### Requirements
- Python 3.8 or higher
- PyAutoGUI for automation
- OpenAI Python SDK
- NVIDIA NIM API access for LLaMA

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
1. Navigate to directory you clone this code
2. To test Krya.ai in action:
```bash
streamlit run src/main.py
```
3. Enter your saved API keys when prompted.
4. Follow the interactive flow to see the orchestration and automation in action.

## Key Features
- 🤖 Multi-LLM Orchestration: Streamlines coordination between GPT and LLaMA.
- 🔄 Automated Prompt Refinement: Uses GPT for prompt optimization and PyAutoGUI for GUI automation.
- ✨ Enhanced Response Generation: Delivers refined and high-quality responses.
- 📊 Error Handling & Feedback Loop: Robust system for catching errors and refining responses dynamically.
- 📈 Performance Metrics: Insights into the performance and reliability of orchestrated automation tasks.

## Code Execution Workflow
### 1. LLM Code Generation
- The LLM generates code snippets based on user instructions.
- Example: If a user asks for a "Hello, World!" script, the LLM can produce:
```bash
print("Hello, World!")
```
### 2. Passing the Code to an Execution Environment
- The generated code is sent to an environment capable of execution. This could be:
- Local Execution: Running code on the user's machine using a Python interpreter.
- Server Execution: Executing code on a secure remote server and returning results.
### 3. Execution Environment Setup
- Configure a local or server-based system to receive, execute, and handle code outputs or errors.
- Common Setup Options:
- Local: Use Python or other interpreters installed on the user’s system.
- Server: Set up a remote server to securely execute code and return results.
### 4. Returning Results to the LLM
- The execution environment sends the output or any errors back to the LLM.
- The LLM uses this feedback for iterative improvements, refining the code as needed.

### Automating Cursor Movement and Interactions
#### 1. Using Automation Libraries
- LLMs can generate scripts for automation tasks such as cursor movement, clicks, and typing. We use PyAutoGUI Library.
#### 2. Script Generation and Execution
#### Example Task: Open a text editor and type "Hello, World!".
LLM-Generated Script:
```bash
import pyautogui
import time

# Open the text editor (this may vary based on the system)
pyautogui.hotkey('win')  # Open the Run dialog
pyautogui.typewrite('notepad\n', interval=0.1)
time.sleep(1)  # Wait for the editor to open

# Type "Hello, World!" in the text editor
pyautogui.typewrite('Hello, World!', interval=0.1)
Execution: Run this script in a Python environment with PyAutoGUI installed. It will automate opening Notepad and typing "Hello, World!".
```

### Use Cases
#### 1. Automated Testing
- Use LLMs to generate and execute test scripts automatically.
#### 2. GUI Automation
- Automate repetitive tasks, such as form filling or software navigation.
