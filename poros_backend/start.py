#!/usr/bin/env python3
"""
Railway startup script - reads PORT from environment
"""
import os
import subprocess

port = os.environ.get("PORT", "8000")
print(f"Starting Poros Protocol on port {port}")

subprocess.run([
    "uvicorn",
    "app.main:app",
    "--host", "0.0.0.0",
    "--port", port
])
