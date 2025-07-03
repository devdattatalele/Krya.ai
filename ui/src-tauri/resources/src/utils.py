import os
import re
import json
import logging
import subprocess
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("krya-utils")

def get_base_dir() -> str:
    """Get the base directory of the application"""
    return os.path.dirname(os.path.abspath(__file__))

def get_full_path(relative_path: str) -> str:
    """Get the full path from a path relative to the base directory"""
    return os.path.join(get_base_dir(), relative_path)

def ensure_dir_exists(dir_path: str) -> None:
    """Ensure a directory exists, creating it if necessary"""
    os.makedirs(dir_path, exist_ok=True)

def is_execution_successful(execution_message: str) -> bool:
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

def requires_interactive_execution(code: str) -> bool:
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

def execute_subprocess(
    cmd: List[str], 
    timeout: int = 30,
    cwd: Optional[str] = None
) -> Tuple[int, str, str]:
    """Execute a subprocess and return exit code, stdout, and stderr"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return 1, "", f"Error executing command: {str(e)}"

def format_execution_result(
    exit_code: int, 
    stdout: str, 
    stderr: str
) -> str:
    """Format execution results into a readable string"""
    execution_output = f"=== EXECUTION RESULTS ===\n"
    execution_output += f"Exit Code: {exit_code}\n"
    execution_output += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    if stdout:
        execution_output += f"STDOUT:\n{stdout}\n"
    
    if stderr:
        execution_output += f"STDERR:\n{stderr}\n"
    
    if exit_code == 0:
        execution_output += "\n✅ Script executed successfully!"
    else:
        execution_output += f"\n❌ Script failed with exit code {exit_code}"
    
    return execution_output

def load_json_config(file_path: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
    """Load a JSON configuration file, returning default if not found"""
    if default is None:
        default = {}
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return default
    except Exception as e:
        logger.error(f"Error loading config from {file_path}: {e}")
        return default

def save_json_config(file_path: str, config: Dict[str, Any]) -> bool:
    """Save configuration to a JSON file"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving config to {file_path}: {e}")
        return False

def is_port_in_use(port: int) -> bool:
    """Check if a port is in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find an available port starting from start_port"""
    port = start_port
    while is_port_in_use(port) and max_attempts > 0:
        port += 1
        max_attempts -= 1
    
    if max_attempts == 0:
        raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")
    
    return port 