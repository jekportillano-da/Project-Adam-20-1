import os
import sys
import uvicorn

if __name__ == "__main__":
    # Start uvicorn with the gateway app
    uvicorn.run(
        "gateway:app", 
        host="0.0.0.0",  # Bind to all interfaces
        port=8080,
        reload=True,
        log_level="debug",
    )
