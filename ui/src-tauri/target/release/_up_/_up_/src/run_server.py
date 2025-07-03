#!/usr/bin/env python3
import uvicorn
import os
import sys
import logging
from utils import find_available_port, is_port_in_use

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("krya-server")

def run_server(host="0.0.0.0", port=8000, reload=False):
    """
    Run the FastAPI server
    
    Args:
        host: Host to run the server on
        port: Port to run the server on
        reload: Whether to reload the server on code changes
    """
    try:
        # Check if the port is in use
        if is_port_in_use(port):
            logger.warning(f"Port {port} is already in use. Finding an available port...")
            port = find_available_port(port)
            logger.info(f"Using port {port} instead")
        
        logger.info(f"Starting Krya.ai API server on http://{host}:{port}")
        uvicorn.run("app:app", host=host, port=port, reload=reload)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the Krya.ai API server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Reload the server on code changes")
    
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs(os.path.join(os.getcwd(), "generated_output"), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), "logs"), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), "config"), exist_ok=True)
    
    run_server(host=args.host, port=args.port, reload=args.reload) 