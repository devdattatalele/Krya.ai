import base64
import pyperclip
import streamlit as st
from functions.gen import generate_code, regenerate_code_with_feedback
from functions.exec import run_script, run_script_with_terminal_fallback
import os
from dotenv import load_dotenv
import re

def process_prompt(prompt, max_retries=3):
    """Enhanced process_prompt with retry logic and error handling"""
    
    for attempt in range(max_retries):
        try:
            st.info(f"🔄 Attempt {attempt + 1}/{max_retries}: Generating code...")
            
            if attempt == 0:
                generated_code = generate_code(prompt)
            else:
                # Use feedback from previous execution for regeneration
                feedback = st.session_state.get('last_execution_result', '')
                generated_code = regenerate_code_with_feedback(prompt, feedback)
            
            st.success("✅ Code generated successfully!")
            
            # Determine execution method based on code content
            if requires_interactive_execution(generated_code):
                st.info("🖥️ Detected interactive script - using terminal execution...")
                execution_message = run_script_with_terminal_fallback()
            else:
                st.info("⚡ Running script with direct execution...")
                execution_message = run_script()
            
            # Store execution result in session state for potential retry
            st.session_state['last_execution_result'] = execution_message
            
            # Check if execution was successful
            if is_execution_successful(execution_message):
                st.success("🎉 Execution completed successfully!")
                return generated_code, execution_message
            else:
                st.warning(f"⚠️ Execution failed on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    st.info("🔄 Will retry with improved code...")
                    continue
                else:
                    st.error("❌ Max retries reached. Please check the code manually.")
                    return generated_code, execution_message
                    
        except Exception as e:
            error_msg = f"❌ Error on attempt {attempt + 1}: {str(e)}"
            st.error(error_msg)
            if attempt == max_retries - 1:
                return "", error_msg
    
    return generated_code, execution_message

def requires_interactive_execution(code):
    """Determine if code requires interactive terminal execution"""
    interactive_patterns = [
        r'input\s*\(',
        r'pyautogui\.',
        r'keyboard\.',
        r'mouse\.',
        r'cv2\.',
        r'webbrowser\.',
    ]
    
    for pattern in interactive_patterns:
        if re.search(pattern, code):
            return True
    return False

def is_execution_successful(execution_message):
    """Check if execution was successful based on the execution message"""
    success_indicators = [
        "✅ Script executed successfully!",
        "Exit Code: 0",
        "Script execution initiated via terminal"
    ]
    
    failure_indicators = [
        "❌",
        "Exit Code: 1",
        "STDERR:",
        "TimeoutExpired",
        "Error"
    ]
    
    # Check for success indicators
    for indicator in success_indicators:
        if indicator in execution_message:
            # Also check that there are no failure indicators
            if not any(fail in execution_message for fail in failure_indicators):
                return True
    
    return False

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def copy_to_clipboard(text, button_key):
    if st.button("📋 Copy", key=button_key):
        pyperclip.copy(text)
        st.success("Copied to clipboard!")

def check_api():
    load_dotenv()
    return bool(os.getenv("GOOGLE_API_KEY"))
