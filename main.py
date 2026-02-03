"""
Salad Cloud GPU Instance - FastAPI Code Execution Server
Provides an endpoint for executing Python code with GPU support.
"""

import os
import sys
import traceback
import asyncio
from io import StringIO
from typing import Optional, Any
from contextlib import redirect_stdout, redirect_stderr

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Get timeout from environment variable (default: 1 hour)
PYTHON_EXECUTE_TIMEOUT = int(os.getenv("PYTHON_EXECUTE_TIMEOUT", "3600"))

app = FastAPI(
    title="GPU Code Execution API",
    description="Execute Python code on Salad Cloud GPU instances",
    version="1.0.0"
)

# CORS middleware for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeExecutionRequest(BaseModel):
    """Request model for code execution."""
    code: str = Field(..., description="Python code to execute")
    timeout: Optional[int] = Field(
        default=None,
        description=f"Execution timeout in seconds (default: {PYTHON_EXECUTE_TIMEOUT})"
    )


class CodeExecutionResponse(BaseModel):
    """Response model for code execution."""
    success: bool
    stdout: str
    stderr: str
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float


async def execute_code_with_timeout(code: str, timeout: int) -> dict:
    """
    Execute Python code with a timeout.
    
    Args:
        code: Python code string to execute
        timeout: Maximum execution time in seconds
        
    Returns:
        Dictionary with execution results
    """
    import time
    start_time = time.time()
    
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    result = None
    error = None
    success = False
    
    # Create a namespace for code execution
    exec_globals = {
        "__builtins__": __builtins__,
        "__name__": "__main__",
    }
    
    try:
        # Compile the code first to catch syntax errors
        compiled_code = compile(code, "<string>", "exec")
        
        # Execute with output capture
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Run in a thread pool to allow timeout
            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    exec,
                    compiled_code,
                    exec_globals
                ),
                timeout=timeout
            )
        
        success = True
        # Check if there's a 'result' variable in the namespace
        if 'result' in exec_globals:
            result = exec_globals['result']
            
    except asyncio.TimeoutError:
        error = f"Execution timed out after {timeout} seconds"
    except SyntaxError as e:
        error = f"Syntax error: {e}"
    except Exception as e:
        error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
    
    execution_time = time.time() - start_time
    
    return {
        "success": success,
        "stdout": stdout_capture.getvalue(),
        "stderr": stderr_capture.getvalue(),
        "result": result,
        "error": error,
        "execution_time": execution_time
    }


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "GPU Code Execution API",
        "default_timeout": PYTHON_EXECUTE_TIMEOUT
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    import torch
    
    gpu_available = torch.cuda.is_available() if 'torch' in sys.modules else False
    gpu_name = torch.cuda.get_device_name(0) if gpu_available else "N/A"
    
    return {
        "status": "healthy",
        "gpu_available": gpu_available,
        "gpu_name": gpu_name,
        "python_version": sys.version,
        "timeout_setting": PYTHON_EXECUTE_TIMEOUT
    }


@app.post("/v1/code/execute/python", response_model=CodeExecutionResponse)
async def execute_python_code(request: CodeExecutionRequest):
    """
    Execute Python code on the GPU instance.
    
    This endpoint accepts Python code and executes it with the configured
    timeout. The code has access to all installed libraries including
    GPU-accelerated ones.
    
    - **code**: The Python code to execute
    - **timeout**: Optional custom timeout (uses PYTHON_EXECUTE_TIMEOUT env var if not set)
    """
    # Use custom timeout or default
    timeout = request.timeout or PYTHON_EXECUTE_TIMEOUT
    
    # Cap timeout at environment maximum for safety
    timeout = min(timeout, PYTHON_EXECUTE_TIMEOUT)
    
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="No code provided")
    
    # Execute the code
    result = await execute_code_with_timeout(request.code, timeout)
    
    return CodeExecutionResponse(**result)


@app.get("/v1/info")
async def get_instance_info():
    """Get information about the GPU instance and available libraries."""
    import pkg_resources
    
    installed_packages = [
        {"name": pkg.key, "version": pkg.version}
        for pkg in pkg_resources.working_set
    ]
    
    # Check for GPU
    try:
        import torch
        gpu_info = {
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        }
    except ImportError:
        gpu_info = {"cuda_available": False, "note": "PyTorch not installed"}
    
    return {
        "python_version": sys.version,
        "gpu_info": gpu_info,
        "installed_packages": installed_packages,
        "environment": {
            "PYTHON_EXECUTE_TIMEOUT": PYTHON_EXECUTE_TIMEOUT,
            "SOUNDFONT_PATH": os.getenv("SOUNDFONT_PATH", "Not set")
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
