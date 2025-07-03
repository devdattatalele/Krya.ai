import os
import google.generativeai as genai
from functions.config import configure_model
import logging
from typing import Optional

# Import from utils
from utils import ensure_dir_exists

logger = logging.getLogger("krya-gen")

def generate_code(prompt: str) -> str:
    """
    Generate code based on a natural language prompt
    
    Args:
        prompt: The natural language prompt
        
    Returns:
        Generated Python code as a string
    """
    try:
        logger.info(f"Generating code for prompt: {prompt[:50]}...")
        model = configure_model()
        
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [prompt],
                },
            ]
        )
        
        response = chat_session.send_message(prompt)
        generated_code = response.text
        
        # Clean the response
        generated_code = clean_code_response(generated_code)
        
        # Save to file
        save_generated_code(generated_code)
        
        logger.info(f"Code generation successful, generated {len(generated_code)} characters")
        return generated_code
    
    except Exception as e:
        logger.error(f"Error generating code: {e}")
        raise

def regenerate_code_with_feedback(original_prompt: str, execution_feedback: str) -> str:
    """
    Generate improved code based on execution feedback
    
    Args:
        original_prompt: The original natural language prompt
        execution_feedback: Feedback from previous execution attempt
        
    Returns:
        Improved Python code as a string
    """
    try:
        logger.info(f"Regenerating code with feedback for prompt: {original_prompt[:50]}...")
        model = configure_model()
        
        feedback_prompt = f"""
        Original Request: {original_prompt}
        
        Previous Execution Result:
        {execution_feedback}
        
        The previous code had issues. Please generate improved Python code that:
        1. Fixes any errors shown in the execution feedback
        2. Uses proper macOS key combinations with keyDown/press/keyUp instead of hotkey
        3. Includes appropriate time.sleep() delays for macOS UI elements
        4. Handles potential edge cases better
        5. Is more robust and reliable
        
        Generate ONLY the Python code without explanations.
        """
        
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user", 
                    "parts": [feedback_prompt],
                },
            ]
        )
        
        response = chat_session.send_message(feedback_prompt)
        improved_code = response.text
        
        # Clean and save improved code
        improved_code = clean_code_response(improved_code)
        save_generated_code(improved_code)
        
        logger.info(f"Code regeneration successful, generated {len(improved_code)} characters")
        return improved_code
    
    except Exception as e:
        logger.error(f"Error regenerating code: {e}")
        raise

def clean_code_response(code_text: str) -> str:
    """
    Clean the LLM response to extract pure Python code
    
    Args:
        code_text: Raw text from the LLM response
        
    Returns:
        Cleaned Python code as a string
    """
    generated_code = code_text
    
    # Remove code block markers
    if generated_code.startswith("```python"):
        generated_code = generated_code[len("```python"):].strip()
    elif generated_code.startswith("```"):
        generated_code = generated_code[3:].strip()
        
    if generated_code.endswith("```"):
        generated_code = generated_code[:-3].strip()

    # Ensure proper imports are present
    if "import pyautogui" not in generated_code and "pyautogui." in generated_code:
        generated_code = "import pyautogui\nimport time\n\n" + generated_code

    return generated_code

def save_generated_code(code: str, file_path: Optional[str] = None) -> str:
    """
    Save generated code to a file
    
    Args:
        code: The code to save
        file_path: Optional path to save the code to. If None, uses default path.
        
    Returns:
        Path where the code was saved
    """
    if file_path is None:
        output_dir = os.path.join(os.getcwd(), "generated_output")
        ensure_dir_exists(output_dir)
        file_path = os.path.join(output_dir, "generated_output.py")
    
    with open(file_path, "w") as f:
        f.write(code)
    
    return file_path
