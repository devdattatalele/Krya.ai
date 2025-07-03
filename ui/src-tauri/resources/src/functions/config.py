import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Optional

# Import from utils
from utils import get_full_path, load_json_config, save_json_config

logger = logging.getLogger("krya-config")

# Default configuration
DEFAULT_CONFIG = {
    "model_name": "gemini-2.5-flash",
        "temperature": 1.55,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

def get_system_instruction() -> str:
    """
    Load the system instruction from file
    
    Returns:
        System instruction as a string
    """
    instruction_path = get_full_path("system/instruction.txt")
    
    try:
        with open(instruction_path, "r", encoding="utf-8") as f:
            instruct = f.read()
        return instruct
    except Exception as e:
        logger.error(f"Error loading system instruction: {e}")
        return ""

def get_api_key() -> Optional[str]:
    """
    Get the API key from environment variables
    
    Returns:
        API key as a string, or None if not found
    """
    # Ensure environment variables are loaded
    load_dotenv()
    return os.getenv("GOOGLE_API_KEY")

def load_model_config() -> Dict[str, Any]:
    """
    Load model configuration from config file or use defaults
    
    Returns:
        Model configuration as a dictionary
    """
    config_path = os.path.join(os.getcwd(), "config", "config.json")
    config = load_json_config(config_path, DEFAULT_CONFIG)
    
    # Ensure all required keys are present
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
    
    return config

def save_model_config(config: Dict[str, Any]) -> bool:
    """
    Save model configuration to config file
    
    Args:
        config: Model configuration as a dictionary
        
    Returns:
        True if successful, False otherwise
    """
    config_path = os.path.join(os.getcwd(), "config", "config.json")
    return save_json_config(config_path, config)

def configure_model() -> genai.GenerativeModel:
    """
    Configure and return a GenerativeModel instance
    
    Returns:
        Configured GenerativeModel instance
    """
    # Get API key
    api_key = get_api_key()
    if not api_key:
        logger.error("API key not found. Please set the GOOGLE_API_KEY environment variable.")
        raise ValueError("API key not found")
    
    # Configure genai with API key
    genai.configure(api_key=api_key)
    
    # Load model configuration
    config = load_model_config()
    
    # Get system instruction
    instruct = get_system_instruction()
    
    # Create generation config
    generation_config = {
        "temperature": config.get("temperature", DEFAULT_CONFIG["temperature"]),
        "top_p": config.get("top_p", DEFAULT_CONFIG["top_p"]),
        "top_k": config.get("top_k", DEFAULT_CONFIG["top_k"]),
        "max_output_tokens": config.get("max_output_tokens", DEFAULT_CONFIG["max_output_tokens"]),
        "response_mime_type": config.get("response_mime_type", DEFAULT_CONFIG["response_mime_type"]),
    }
    
    # Create and return model
    model = genai.GenerativeModel(
        model_name=config.get("model_name", DEFAULT_CONFIG["model_name"]),
        generation_config=generation_config,
        system_instruction=instruct,
    )
    
    logger.info(f"Model configured: {config.get('model_name', DEFAULT_CONFIG['model_name'])}")
    return model
