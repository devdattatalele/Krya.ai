import os
import time
import pyautogui
import subprocess
import tempfile
from datetime import datetime
import logging
from typing import Dict, Any, Tuple, Optional
import uuid
import signal
import sys

# Import from utils
from utils import format_execution_result, execute_subprocess

logger = logging.getLogger("krya-exec")

def run_script(script_path: Optional[str] = None) -> str:
    """
    Execute a Python script directly using subprocess
    
    Args:
        script_path: Path to the script to execute. If None, uses default path.
        
    Returns:
        Formatted execution result as a string
    """
    try:
        if script_path is None:
            script_path = os.path.join(os.getcwd(), "generated_output", "generated_output.py")
        
        # Ensure the script exists
        if not os.path.exists(script_path):
            return f"❌ Script not found at {script_path}"
        
        # Execute the script using subprocess
        exit_code, stdout, stderr = execute_subprocess(
            ["python3", script_path],
            timeout=30
        )
        
        # Format and return the result
        return format_execution_result(exit_code, stdout, stderr)
            
    except Exception as e:
        logger.error(f"Error in run_script: {e}")
        return f"❌ An error occurred during script execution: {str(e)}"

def run_script_with_terminal_fallback(script_path: Optional[str] = None) -> str:
    """
    Fallback method using terminal automation for interactive scripts
    
    Args:
        script_path: Path to the script to execute. If None, uses default path.
        
    Returns:
        Status message
    """
    try:
        if script_path is None:
            script_path = os.path.join(os.getcwd(), "generated_output", "generated_output.py")
        
        # Ensure the script exists
        if not os.path.exists(script_path):
            return f"❌ Script not found at {script_path}"
        
        # Use macOS key handling method for Spotlight
        pyautogui.keyDown('command')
        pyautogui.press('space')
        pyautogui.keyUp('command')
        time.sleep(1)
        
        pyautogui.typewrite('terminal', interval=0.1)
        pyautogui.press('enter')
        time.sleep(2)
        
        # Open new terminal tab with correct macOS key handling
        pyautogui.keyDown('command')
        pyautogui.press('t')
        pyautogui.keyUp('command')
        time.sleep(2)
        
        # Run the script
        pyautogui.typewrite(f'python3 "{script_path}"', interval=0.01)
        pyautogui.press('enter')
        
        time.sleep(3)  # Give time for execution
        
        return "Script execution initiated via terminal. Check terminal window for results."
        
    except Exception as e:
        logger.error(f"Error in run_script_with_terminal_fallback: {e}")
        return f"❌ Terminal execution failed: {str(e)}"

def run_script_async(script_path: Optional[str] = None) -> Tuple[subprocess.Popen, str]:
    """
    Execute a Python script asynchronously and return the process object
    
    Args:
        script_path: Path to the script to execute. If None, uses default path.
        
    Returns:
        Tuple of (process object, log file path)
    """
    try:
        if script_path is None:
            script_path = os.path.join(os.getcwd(), "generated_output", "generated_output.py")
        
        # Ensure the script exists
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found at {script_path}")
        
        # Create a log file
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # Start the process
        with open(log_file, "w") as f:
            # Add a timeout wrapper script with one-time execution flag
            wrapper_script = f"""
import sys
import os
import time
import signal
import subprocess
import uuid
import tempfile

# Generate a unique execution ID for this run
EXECUTION_ID = str(uuid.uuid4())

# Create flag files in system temp directory for better isolation
TEMP_DIR = tempfile.gettempdir()
FLAG_FILE = os.path.join(TEMP_DIR, "krya_execution.lock")
EXEC_FLAG_FILE = os.path.join(TEMP_DIR, "krya_execution_id.txt")
TIMESTAMP_FILE = os.path.join(TEMP_DIR, "krya_last_run.txt")

# Check if another instance is running
if os.path.exists(FLAG_FILE):
    # Check if the flag file is stale (older than 30 seconds)
    if time.time() - os.path.getmtime(FLAG_FILE) > 30:
        print("Found stale lock file, removing it")
        os.remove(FLAG_FILE)
    else:
        print("Another execution is already in progress. Exiting.")
        sys.exit(0)

# Create the flag file
with open(FLAG_FILE, 'w') as ff:
    ff.write(str(time.time()))
print(f"Created lock file: {{FLAG_FILE}}")

# Store the execution ID
with open(EXEC_FLAG_FILE, 'w') as ef:
    ef.write(EXECUTION_ID)

# Update timestamp
with open(TIMESTAMP_FILE, 'w') as tf:
    tf.write(str(time.time()))

def cleanup_flag():
    """Remove flag files on exit"""
    try:
        for file in [FLAG_FILE, EXEC_FLAG_FILE, TIMESTAMP_FILE]:
            if os.path.exists(file):
                os.remove(file)
                print(f"Removed flag file: {{file}}")
    except Exception as e:
        print(f"Error during cleanup: {{e}}")

def timeout_handler(signum, frame):
    """Handle timeout signal"""
    print("Script execution timed out after 30 seconds")
    cleanup_flag()
    # Kill any child processes
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(os.getpid())], 
                          stderr=subprocess.DEVNULL)
        else:  # Unix/Linux/Mac
            # More aggressive process killing for macOS
            subprocess.run(['pkill', '-P', str(os.getpid())], 
                          stderr=subprocess.DEVNULL)
            # Also try to kill any Python processes running our script
            subprocess.run(['pkill', '-f', 'generated_output.py'], 
                          stderr=subprocess.DEVNULL)
    except:
        pass
    sys.exit(1)

# Set timeout handler
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

try:
    # Execute the actual script with the execution ID as an environment variable
    env = os.environ.copy()
    env['KRYA_EXECUTION_ID'] = EXECUTION_ID
    
    print(f"Executing script: {{{script_path}}}")
    print(f"Execution ID: {{EXECUTION_ID}}")
    print(f"Start time: {{time.strftime('%Y-%m-%d %H:%M:%S')}}")
    
    result = subprocess.run(
        [sys.executable, "{script_path}"], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True,
        check=False,
        env=env
    )
    
    # Print output
    print(result.stdout)
    if result.stderr:
        print("ERRORS:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
    
    # Exit with the same code
    print(f"Execution complete. Exit code: {{result.returncode}}")
    print(f"End time: {{time.strftime('%Y-%m-%d %H:%M:%S')}}")
    cleanup_flag()
    sys.exit(result.returncode)
except Exception as e:
    print(f"Error executing script: {{e}}")
    cleanup_flag()
    sys.exit(1)
finally:
    # Cancel the alarm
    signal.alarm(0)
    cleanup_flag()
"""
            # Create a temporary wrapper script
            import tempfile
            wrapper_fd, wrapper_path = tempfile.mkstemp(suffix='.py')
            with os.fdopen(wrapper_fd, 'w') as wrapper_file:
                wrapper_file.write(wrapper_script)
            
            # Execute the wrapper script instead
            process = subprocess.Popen(
                ["python3", wrapper_path],
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Store the wrapper path to clean up later
            process._wrapper_path = wrapper_path
        
        return process, log_file
        
    except Exception as e:
        logger.error(f"Error in run_script_async: {e}")
        raise
