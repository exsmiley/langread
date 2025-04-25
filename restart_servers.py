#!/usr/bin/env python3
"""
Server management script for LangRead application.
This script can:
1. Kill any existing server processes
2. Start the API server and frontend server
3. Check the status of running servers
"""

import os
import sys
import subprocess
import time
import signal
import argparse
from typing import List, Dict, Optional
import socket
import psutil

# Configuration
API_PORT = 8001
FRONTEND_PORT = 8080
SERVER_INFO = {
    "api": {
        "name": "API Server",
        "port": API_PORT,
        "start_cmd": ["python", "-m", "uvicorn", "main:app", "--reload", "--port", str(API_PORT)],
        "cwd": "src/api",
        "pid_file": ".api_server.pid"
    },
    "frontend": {
        "name": "Frontend Server",
        "port": FRONTEND_PORT,
        "start_cmd": ["python", "-m", "http.server", str(FRONTEND_PORT)],
        "cwd": "src/frontend",
        "pid_file": ".frontend_server.pid"
    }
}


def is_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def find_processes_using_port(port: int) -> List[int]:
    """Find all process IDs using the specified port using lsof."""
    try:
        output = subprocess.check_output(['lsof', '-i', f':{port}', '-t'], text=True)
        return [int(pid) for pid in output.strip().split('\n') if pid.strip()]
    except subprocess.CalledProcessError:
        # No processes found or command failed
        return []


def kill_process(pid: int) -> bool:
    """Kill a process by its PID."""
    try:
        os.kill(pid, signal.SIGTERM)
        # Wait a moment and check if it's still running
        time.sleep(0.5)
        if psutil.pid_exists(pid):
            os.kill(pid, signal.SIGKILL)
        return True
    except Exception as e:
        print(f"Error killing process {pid}: {e}")
        return False


def save_pid(server_type: str, pid: int):
    """Save PID to file for later cleanup."""
    with open(SERVER_INFO[server_type]["pid_file"], 'w') as f:
        f.write(str(pid))


def load_pid(server_type: str) -> Optional[int]:
    """Load PID from file if it exists."""
    pid_file = SERVER_INFO[server_type]["pid_file"]
    if os.path.exists(pid_file):
        with open(pid_file, 'r') as f:
            try:
                return int(f.read().strip())
            except:
                return None
    return None


def kill_server(server_type: str) -> bool:
    """Kill a specific server."""
    server = SERVER_INFO[server_type]
    port = server["port"]
    name = server["name"]
    
    print(f"Stopping {name} (port {port})...")
    
    # Try to kill by stored PID first
    pid = load_pid(server_type)
    if pid and psutil.pid_exists(pid):
        print(f"  Found stored process (PID: {pid})")
        if kill_process(pid):
            print(f"  Killed process {pid}")
            if os.path.exists(server["pid_file"]):
                os.remove(server["pid_file"])
    
    # Check if port is still in use
    if is_port_in_use(port):
        print(f"  Port {port} still in use, finding processes...")
        pids = find_processes_using_port(port)
        for pid in pids:
            print(f"  Killing process with PID {pid}")
            kill_process(pid)
    
    # Verify port is free
    if is_port_in_use(port):
        print(f"  Failed to free port {port}!")
        return False
    else:
        print(f"  {name} stopped successfully!")
        return True


def start_server(server_type: str) -> bool:
    """Start a specific server."""
    server = SERVER_INFO[server_type]
    name = server["name"]
    port = server["port"]
    
    # Ensure port is free
    if is_port_in_use(port):
        print(f"Cannot start {name}: Port {port} is already in use!")
        return False
    
    print(f"Starting {name} on port {port}...")
    
    cwd = server.get("cwd", os.getcwd())
    process = subprocess.Popen(
        server["start_cmd"],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Save PID for later reference
    save_pid(server_type, process.pid)
    
    # Give it a moment to start
    time.sleep(2)
    
    # Check if it started successfully
    if process.poll() is not None:
        print(f"  Error starting {name}:")
        output, _ = process.communicate()
        print(output)
        return False
    
    print(f"  {name} started successfully (PID: {process.pid})")
    return True


def check_servers():
    """Check the status of all servers."""
    all_running = True
    
    for server_type, info in SERVER_INFO.items():
        port = info["port"]
        name = info["name"]
        
        if is_port_in_use(port):
            pids = find_processes_using_port(port)
            pid_str = ", ".join(str(p) for p in pids) if pids else "Unknown"
            print(f"✅ {name} is RUNNING on port {port} (PID: {pid_str})")
        else:
            print(f"❌ {name} is NOT RUNNING")
            all_running = False
    
    return all_running


def install_dependencies():
    """Install required dependencies."""
    print("Installing required dependencies...")
    
    # List of required packages
    requirements = [
        "fastapi", "uvicorn", "feedparser", "newspaper3k", "psutil",
        "langchain", "openai"
    ]
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install"] + requirements, check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="LangRead Server Management")
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'install'], 
                        help="Action to perform")
    parser.add_argument('--api-only', action='store_true', help="Only manage API server")
    parser.add_argument('--frontend-only', action='store_true', help="Only manage frontend server")
    
    args = parser.parse_args()
    
    # Determine which servers to manage
    servers_to_manage = []
    if args.api_only:
        servers_to_manage = ["api"]
    elif args.frontend_only:
        servers_to_manage = ["frontend"]
    else:
        servers_to_manage = ["api", "frontend"]
    
    # Install dependencies if requested
    if args.action == 'install':
        install_dependencies()
        return
    
    # Check status if requested
    if args.action == 'status':
        check_servers()
        return
    
    # Stop servers if requested
    if args.action in ['stop', 'restart']:
        for server_type in servers_to_manage:
            kill_server(server_type)
    
    # Start servers if requested
    if args.action in ['start', 'restart']:
        for server_type in servers_to_manage:
            start_server(server_type)
    
    # Display final status
    if args.action in ['start', 'restart']:
        print("\nServer Status:")
        check_servers()
        
        print("\nAccess URLs:")
        if "api" in servers_to_manage:
            print(f"API Documentation: http://localhost:{API_PORT}/docs")
        if "frontend" in servers_to_manage:
            print(f"Frontend: http://localhost:{FRONTEND_PORT}")


if __name__ == "__main__":
    # Check for required package psutil
    try:
        import psutil
    except ImportError:
        print("Missing required package 'psutil'. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], check=True)
        print("psutil installed. Restarting script...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    main()
