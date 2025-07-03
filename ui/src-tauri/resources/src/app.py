from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import os
import json
import psutil
import asyncio
from typing import Optional, Dict, List, Any, Union
import subprocess
import uuid
import time
from datetime import datetime
import logging
from contextlib import asynccontextmanager

# Import existing functionality
from functions.gen import generate_code, regenerate_code_with_feedback, clean_code_response
from functions.exec import run_script, run_script_async
from functions.config import configure_model
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("krya-api")

# Global state management
class AppState:
    def __init__(self):
        self.active_processes: Dict[str, Dict] = {}  # Map of job_id to process info
        self.recent_logs: List[Dict] = []  # Limited list of recent logs
        self.connected_clients: List[WebSocket] = []  # Active WebSocket connections
        self.recent_prompts: Dict[str, float] = {}  # Map of prompt hash to timestamp
        self.prompt_cooldown = 5.0  # Seconds to wait before allowing the same prompt again
        
    def add_log(self, log_entry: Dict):
        """Add a log entry and broadcast to all connected clients"""
        self.recent_logs.append(log_entry)
        # Keep only the last 100 logs
        if len(self.recent_logs) > 100:
            self.recent_logs = self.recent_logs[-100:]
        # Broadcast to all connected clients
        asyncio.create_task(self.broadcast_log(log_entry))
    
    async def broadcast_log(self, log_entry: Dict):
        """Send log to all connected WebSocket clients"""
        for client in self.connected_clients:
            try:
                await client.send_json(log_entry)
            except Exception as e:
                logger.error(f"Failed to send log to client: {e}")
                # Will be removed in the connection handler
    
    def check_prompt_cooldown(self, prompt: str) -> bool:
        """
        Check if this prompt was recently executed
        Returns True if prompt is allowed, False if it's too soon
        """
        import hashlib
        # Create a hash of the prompt to use as key
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        
        current_time = time.time()
        if prompt_hash in self.recent_prompts:
            last_time = self.recent_prompts[prompt_hash]
            if current_time - last_time < self.prompt_cooldown:
                # Too soon to run the same prompt again
                return False
        
        # Update the timestamp for this prompt
        self.recent_prompts[prompt_hash] = current_time
        
        # Clean up old entries
        self.recent_prompts = {k: v for k, v in self.recent_prompts.items() 
                             if current_time - v < 300}  # Keep entries for 5 minutes
        
        return True

app_state = AppState()

# Define lifespan to handle startup/shutdown tasks
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load environment variables
    load_dotenv()
    # Check if config directory exists
    os.makedirs(os.path.join(os.getcwd(), "config"), exist_ok=True)
    
    # Clean up any stale flag files on startup
    try:
        cleanup_all_processes()
        logger.info("Cleaned up flag files and processes on startup")
    except Exception as e:
        logger.error(f"Error cleaning up on startup: {e}")
    
    # Yield control to the application
    yield
    
    # Shutdown: Clean up any running processes
    for job_id, process_info in list(app_state.active_processes.items()):
        try:
            process = process_info.get("process")
            if process and process.poll() is None:
                process.terminate()
                logger.info(f"Terminated process for job {job_id}")
        except Exception as e:
            logger.error(f"Error terminating process for job {job_id}: {e}")
    
    # Final cleanup of any remaining processes and flag files
    try:
        cleanup_all_processes()
        logger.info("Cleaned up flag files and processes on shutdown")
    except Exception as e:
        logger.error(f"Error cleaning up on shutdown: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="Krya.ai API",
    description="API for Krya.ai automation system",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for the Tauri UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class PromptRequest(BaseModel):
    prompt: str = Field(..., description="The natural language prompt to process")
    max_retries: int = Field(3, description="Maximum number of retry attempts")

class StopRequest(BaseModel):
    job_id: str = Field(..., description="ID of the job to stop")

class ConfigUpdateRequest(BaseModel):
    api_key: Optional[str] = Field(None, description="Google Gemini API key")
    model_name: Optional[str] = Field(None, description="Model name to use")
    temperature: Optional[float] = Field(None, description="Temperature for generation")
    max_output_tokens: Optional[int] = Field(None, description="Maximum output tokens")
    top_p: Optional[float] = Field(None, description="Top-p sampling parameter")
    top_k: Optional[int] = Field(None, description="Top-k sampling parameter")

# --- Helper Functions ---

def save_config(config: Dict[str, Any]):
    """Save configuration to a JSON file"""
    config_path = os.path.join(os.getcwd(), "config", "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    # Also update .env file for API key
    if "api_key" in config and config["api_key"]:
        env_path = os.path.join(os.getcwd(), ".env")
        with open(env_path, "w") as f:
            f.write(f"GOOGLE_API_KEY={config['api_key']}")

def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file"""
    config_path = os.path.join(os.getcwd(), "config", "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    
    # Default config
    default_config = {
        "api_key": os.getenv("GOOGLE_API_KEY", ""),
        "model_name": "gemini-2.5-flash",
        "temperature": 1.55,
        "max_output_tokens": 8192,
        "top_p": 0.95,
        "top_k": 40
    }
    
    # Save default config
    save_config(default_config)
    return default_config

async def execute_automation(job_id: str, prompt: str, max_retries: int = 3):
    """Execute the automation process and update state"""
    if job_id not in app_state.active_processes:
        logger.error(f"Job {job_id} not found in active processes")
        return
    
    # Create a unique execution ID for this job
    execution_id = str(uuid.uuid4())
    app_state.active_processes[job_id]["execution_id"] = execution_id
    
    try:
        # Clean up any stale flag files before starting
        flag_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".execution_in_progress")
        if os.path.exists(flag_file) and time.time() - os.path.getmtime(flag_file) > 60:
            try:
                os.unlink(flag_file)
                logger.info("Removed stale execution flag file")
            except Exception as e:
                logger.error(f"Error removing stale flag file: {e}")
    except Exception as e:
        logger.error(f"Error during pre-execution cleanup: {e}")
        
    for attempt in range(max_retries):
        # Check if job was stopped
        if app_state.active_processes[job_id].get("status") == "stopped":
            logger.info(f"Job {job_id} was stopped, aborting execution")
            return
            
        try:
            # Log the attempt
            app_state.add_log({
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"Attempt {attempt + 1}/{max_retries}: Generating code..."
            })
            
            # Generate code
            if attempt == 0:
                generated_code = generate_code(prompt)
            else:
                # Use feedback from previous execution
                feedback = app_state.active_processes[job_id].get("last_result", "")
                generated_code = regenerate_code_with_feedback(prompt, feedback)
            
            # Save the generated code
            app_state.active_processes[job_id]["code"] = generated_code
            app_state.add_log({
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                "level": "SUCCESS",
                "message": "Code generated successfully!"
            })
            
            # Check if job was stopped
            if app_state.active_processes[job_id].get("status") == "stopped":
                logger.info(f"Job {job_id} was stopped after code generation")
                return
            
            # Execute the code
            app_state.add_log({
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Running script with direct execution..."
            })
            
            # Run the script asynchronously and store the process
            try:
                process, log_file = run_script_async()
                app_state.active_processes[job_id]["process"] = process
                app_state.active_processes[job_id]["log_file"] = log_file
                
                # Wait for process to complete or timeout
                try:
                    exit_code = process.wait(timeout=60)  # 60 second timeout
                    
                    # Check if job was stopped during execution
                    if app_state.active_processes[job_id].get("status") == "stopped":
                        logger.info(f"Job {job_id} was stopped during execution")
                        return
                    
                    # Read log file for output
                    with open(log_file, "r") as f:
                        output = f.read()
                    
                    execution_result = f"Exit code: {exit_code}\n\nOutput:\n{output}"
                    
                    # Clean up temporary wrapper script if it exists
                    if hasattr(process, '_wrapper_path') and os.path.exists(process._wrapper_path):
                        try:
                            os.unlink(process._wrapper_path)
                        except Exception as e:
                            logger.error(f"Error cleaning up wrapper script: {e}")
                    
                    # Clean up any execution flag files that might have been created
                    flag_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".execution_in_progress")
                    if os.path.exists(flag_file):
                        try:
                            os.unlink(flag_file)
                        except Exception as e:
                            logger.error(f"Error cleaning up flag file: {e}")
                    
                    # Clean up any script flag files
                    script_flag = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_output", ".script_executed")
                    if os.path.exists(script_flag):
                        try:
                            os.unlink(script_flag)
                        except Exception as e:
                            logger.error(f"Error cleaning up script flag: {e}")
                    
                    # Clean up timestamp file
                    timestamp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_output", ".last_run_timestamp")
                    if os.path.exists(timestamp_file):
                        try:
                            os.unlink(timestamp_file)
                        except Exception as e:
                            logger.error(f"Error cleaning up timestamp file: {e}")
                            
                except subprocess.TimeoutExpired:
                    # Process took too long, kill it
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        
                    # Also kill any child processes that might be running
                    try:
                        if os.name == 'nt':  # Windows
                            subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                                          stderr=subprocess.DEVNULL)
                        else:  # Unix/Linux/Mac
                            # More aggressive process killing for macOS
                            subprocess.run(['pkill', '-P', str(process.pid)], 
                                          stderr=subprocess.DEVNULL)
                            # Also try to kill any Python processes running our script
                            subprocess.run(['pkill', '-f', 'generated_output.py'], 
                                          stderr=subprocess.DEVNULL)
                            # Kill any PyAutoGUI processes
                            subprocess.run(['pkill', '-f', 'pyautogui'], 
                                          stderr=subprocess.DEVNULL)
                    except Exception as e:
                        logger.error(f"Error killing child processes: {e}")
                    
                    execution_result = "❌ Execution timed out after 60 seconds"
                    
                    # Clean up temporary wrapper script if it exists
                    if hasattr(process, '_wrapper_path') and os.path.exists(process._wrapper_path):
                        try:
                            os.unlink(process._wrapper_path)
                        except Exception as e:
                            logger.error(f"Error cleaning up wrapper script: {e}")
                    
                    # Clean up any execution flag files that might have been created
                    flag_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".execution_in_progress")
                    if os.path.exists(flag_file):
                        try:
                            os.unlink(flag_file)
                        except Exception as e:
                            logger.error(f"Error cleaning up flag file: {e}")
                    
                    # Clean up any script flag files
                    script_flag = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_output", ".script_executed")
                    if os.path.exists(script_flag):
                        try:
                            os.unlink(script_flag)
                        except Exception as e:
                            logger.error(f"Error cleaning up script flag: {e}")
                    
                    # Clean up timestamp file
                    timestamp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_output", ".last_run_timestamp")
                    if os.path.exists(timestamp_file):
                        try:
                            os.unlink(timestamp_file)
                        except Exception as e:
                            logger.error(f"Error cleaning up timestamp file: {e}")
            except Exception as e:
                # Fallback to synchronous execution if async fails
                logger.error(f"Async execution failed: {e}, falling back to sync execution")
                execution_result = run_script()
            
            app_state.active_processes[job_id]["last_result"] = execution_result
            
            # Check if execution was successful
            if "✅" in execution_result or "successful" in execution_result.lower():
                app_state.add_log({
                    "job_id": job_id,
                    "timestamp": datetime.now().isoformat(),
                    "level": "SUCCESS",
                    "message": "Execution completed successfully!"
                })
                app_state.active_processes[job_id]["status"] = "completed"
                
                # Final cleanup of any remaining processes
                cleanup_all_processes()
                return
            else:
                app_state.add_log({
                    "job_id": job_id,
                    "timestamp": datetime.now().isoformat(),
                    "level": "WARNING",
                    "message": f"Execution failed on attempt {attempt + 1}"
                })
                
                if attempt < max_retries - 1 and app_state.active_processes[job_id].get("status") != "stopped":
                    app_state.add_log({
                        "job_id": job_id,
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": "Will retry with improved code..."
                    })
                    continue
                else:
                    app_state.add_log({
                        "job_id": job_id,
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": "Max retries reached. Please check the code manually."
                    })
                    if app_state.active_processes[job_id].get("status") != "stopped":
                        app_state.active_processes[job_id]["status"] = "failed"
                    
                    # Final cleanup of any remaining processes
                    cleanup_all_processes()
                    return
                
        except Exception as e:
            error_msg = f"Error on attempt {attempt + 1}: {str(e)}"
            app_state.add_log({
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "message": error_msg
            })
            
            if attempt == max_retries - 1:
                app_state.active_processes[job_id]["status"] = "failed"
                
                # Final cleanup of any remaining processes
                cleanup_all_processes()
                return

def cleanup_all_processes():
    """Kill any lingering processes and clean up flag files"""
    try:
        # Kill any Python processes that might be running our script
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', 'WINDOWTITLE eq generated_output.py'], 
                          stderr=subprocess.DEVNULL)
        else:  # Unix/Linux/Mac
            # Find and kill any Python processes that might be running our script
            subprocess.run(['pkill', '-f', 'generated_output.py'], stderr=subprocess.DEVNULL)
            # Also try to kill any PyAutoGUI processes
            subprocess.run(['pkill', '-f', 'pyautogui'], stderr=subprocess.DEVNULL)
        
        # Clean up any execution flag files
        flag_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".execution_in_progress")
        if os.path.exists(flag_file):
            os.unlink(flag_file)
        
        # Clean up any script flag files
        script_flag = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_output", ".script_executed")
        if os.path.exists(script_flag):
            os.unlink(script_flag)
        
        # Clean up timestamp file
        timestamp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_output", ".last_run_timestamp")
        if os.path.exists(timestamp_file):
            os.unlink(timestamp_file)
            
    except Exception as e:
        logger.error(f"Error in cleanup_all_processes: {e}")

# --- API Endpoints ---

@app.get("/")
async def root():
    """Root endpoint for API health check"""
    return {"status": "online", "service": "Krya.ai API"}

@app.post("/run")
async def run_automation(
    request: PromptRequest, 
    background_tasks: BackgroundTasks
):
    """Run automation based on a natural language prompt"""
    # Check if API key is configured
    config = load_config()
    if not config.get("api_key"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key not configured. Please set up your API key first."
        )
    
    # Check if this prompt was recently executed
    if not app_state.check_prompt_cooldown(request.prompt):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="This prompt was executed too recently. Please wait a few seconds before trying again."
        )
    
    # Check for any active jobs with the same prompt
    for job_id, job_info in app_state.active_processes.items():
        if (job_info.get("prompt") == request.prompt and 
            job_info.get("status") == "running" and
            (datetime.now() - datetime.fromisoformat(job_info.get("start_time"))).total_seconds() < 60):
            
            return {"job_id": job_id, "status": "running", "message": "This prompt is already being processed"}
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job in active processes
    app_state.active_processes[job_id] = {
        "prompt": request.prompt,
        "status": "running",
        "start_time": datetime.now().isoformat(),
        "code": None,
        "last_result": None
    }
    
    # Log the start of the job
    app_state.add_log({
        "job_id": job_id,
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "message": f"Starting automation job with prompt: {request.prompt}"
    })
    
    # Run the automation in the background
    background_tasks.add_task(
        execute_automation, 
        job_id=job_id, 
        prompt=request.prompt,
        max_retries=request.max_retries
    )
    
    return {"job_id": job_id, "status": "running"}

@app.post("/stop")
async def stop_automation(request: StopRequest):
    """Stop a running automation job"""
    if request.job_id not in app_state.active_processes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {request.job_id} not found"
        )
    
    job_info = app_state.active_processes[request.job_id]
    job_info["status"] = "stopped"  # Mark as stopped immediately
    
    # Log the stop request
    app_state.add_log({
        "job_id": request.job_id,
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "message": "Stopping job by user request..."
    })
    
    # Check if the job has a process that can be terminated
    if "process" in job_info and job_info["process"]:
        try:
            # Try to terminate the process
            if job_info["process"].poll() is None:
                job_info["process"].terminate()
                
                # Wait a bit and kill if still running
                time.sleep(0.5)
                if job_info["process"].poll() is None:
                    if os.name == 'nt':  # Windows
                        job_info["process"].kill()
                        # Also kill any child processes
                        subprocess.run(['taskkill', '/F', '/T', '/PID', str(job_info["process"].pid)], 
                                      stderr=subprocess.DEVNULL)
                    else:  # Unix/Linux/Mac
                        import signal
                        try:
                            os.killpg(os.getpgid(job_info["process"].pid), signal.SIGKILL)
                        except:
                            job_info["process"].kill()
                        
                        # More aggressive process killing for macOS
                        try:
                            subprocess.run(['pkill', '-P', str(job_info["process"].pid)], 
                                          stderr=subprocess.DEVNULL)
                            # Also kill any Python processes that might be running our script
                            subprocess.run(['pkill', '-f', 'generated_output.py'], 
                                          stderr=subprocess.DEVNULL)
                        except Exception as e:
                            logger.error(f"Error killing child processes: {e}")
            
            app_state.add_log({
                "job_id": request.job_id,
                "timestamp": datetime.now().isoformat(),
                "level": "SUCCESS",
                "message": "Job terminated successfully"
            })
            
            # Clean up any temporary files
            if hasattr(job_info["process"], '_wrapper_path') and os.path.exists(job_info["process"]._wrapper_path):
                try:
                    os.unlink(job_info["process"]._wrapper_path)
                except Exception as e:
                    logger.error(f"Error cleaning up wrapper script: {e}")
            
            # Clean up any execution flag files
            flag_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".execution_in_progress")
            if os.path.exists(flag_file):
                try:
                    os.unlink(flag_file)
                except Exception as e:
                    logger.error(f"Error cleaning up flag file: {e}")
                    
        except Exception as e:
            app_state.add_log({
                "job_id": request.job_id,
                "timestamp": datetime.now().isoformat(),
                "level": "WARNING",
                "message": f"Error while terminating process: {str(e)}"
            })
            logger.error(f"Failed to terminate process: {e}")
    else:
        app_state.add_log({
            "job_id": request.job_id,
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "No active process found to terminate"
        })
    
    # Additionally, try to kill any PyAutoGUI processes that might be running
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', 'WINDOWTITLE eq generated_output.py'], stderr=subprocess.DEVNULL)
        else:  # Unix/Linux/Mac
            # Find and kill any Python processes that might be running our script
            subprocess.run(['pkill', '-f', 'generated_output.py'], stderr=subprocess.DEVNULL)
            # Also try to kill any PyAutoGUI processes
            subprocess.run(['pkill', '-f', 'pyautogui'], stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.error(f"Failed to kill additional processes: {e}")
    
    return {"status": "stopped", "job_id": request.job_id}

@app.get("/status")
async def get_status():
    """Get the current system status"""
    # Count jobs by status
    status_counts = {"running": 0, "completed": 0, "failed": 0, "stopped": 0}
    for job in app_state.active_processes.values():
        status = job.get("status", "unknown")
        if status in status_counts:
            status_counts[status] += 1
    
    # Get the most recent logs (limited to 20)
    recent_logs = app_state.recent_logs[-20:] if app_state.recent_logs else []
    
    # Get active jobs
    active_jobs = {
        job_id: {
            "prompt": info["prompt"],
            "status": info["status"],
            "start_time": info["start_time"]
        }
        for job_id, info in app_state.active_processes.items()
        if info["status"] == "running"
    }
    
    return {
        "status": "online",
        "job_counts": status_counts,
        "active_jobs": active_jobs,
        "recent_logs": recent_logs
    }

@app.get("/config")
async def get_config():
    """Get the current configuration"""
    config = load_config()
    # Mask the API key for security
    if "api_key" in config and config["api_key"]:
        config["api_key_set"] = True
        config["api_key"] = "••••••••" + config["api_key"][-4:] if len(config["api_key"]) > 4 else "••••••••"
    else:
        config["api_key_set"] = False
    
    return config

@app.post("/config")
async def update_config(request: ConfigUpdateRequest):
    """Update the configuration"""
    # Load existing config
    config = load_config()
    
    # Update with new values
    for field, value in request.dict(exclude_unset=True).items():
        if value is not None:  # Only update fields that were provided
            config[field] = value
    
    # Save the updated config
    save_config(config)
    
    return {"status": "success", "message": "Configuration updated successfully"}

@app.websocket("/logs")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time logs"""
    await websocket.accept()
    
    # Add client to the list of connected clients
    app_state.connected_clients.append(websocket)
    
    try:
        # Send the last 20 logs immediately upon connection
        recent_logs = app_state.recent_logs[-20:] if app_state.recent_logs else []
        for log in recent_logs:
            await websocket.send_json(log)
        
        # Keep the connection alive and handle incoming messages
        while True:
            # Wait for any message (can be used for ping/pong)
            data = await websocket.receive_text()
            # Simple echo for now
            await websocket.send_json({"echo": data})
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Remove client from the list when disconnected
        if websocket in app_state.connected_clients:
            app_state.connected_clients.remove(websocket)

# Run the app with uvicorn when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 