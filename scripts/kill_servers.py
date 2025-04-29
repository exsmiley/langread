#!/usr/bin/env python3
"""
Simple script to kill all LangRead server processes.
This will terminate any processes running on the API port (8001) and frontend port (8080).
"""

import os
import subprocess
import sys
import signal
import time
import socket

# Configuration
API_PORT = 8000
FRONTEND_PORT = 5173
MONGODB_PORT = 27017


def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def find_processes_using_port(port):
    """Find all process IDs using the specified port using lsof"""
    try:
        output = subprocess.check_output(['lsof', '-i', f':{port}', '-t'], text=True)
        return [int(pid) for pid in output.strip().split('\n') if pid.strip()]
    except subprocess.CalledProcessError:
        # No processes found or command failed
        return []


def kill_server(port, name):
    """Kill all processes using the specified port"""
    print(f"Looking for {name} processes on port {port}...")
    
    if is_port_in_use(port):
        pids = find_processes_using_port(port)
        if pids:
            print(f"Found {len(pids)} process(es) using port {port}")
            for pid in pids:
                print(f"Killing process {pid}")
                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.5)  # Give it a moment to shut down gracefully
                    
                    # If still running, force kill
                    try:
                        os.kill(pid, 0)  # Check if process exists
                        print(f"Process {pid} still running, sending SIGKILL")
                        os.kill(pid, signal.SIGKILL)
                    except OSError:
                        pass  # Process already terminated
                        
                except OSError as e:
                    print(f"Error killing process {pid}: {e}")
        else:
            print(f"Port {port} is in use but couldn't identify the process")
            
        # Verify port is now available
        if is_port_in_use(port):
            print(f"⚠️ Port {port} is still in use!")
        else:
            print(f"✅ Port {port} has been freed")
    else:
        print(f"✅ Port {port} is already free")


def main():
    """Main function to kill all server processes"""
    # Kill API server
    kill_server(API_PORT, "API server")
    
    # Kill frontend server - note that Vite uses hot reload
    # so we may want to keep it running and just restart the API
    if '--all' in sys.argv:
        kill_server(FRONTEND_PORT, "Frontend server")
    
    # MongoDB server if running locally
    if '--db' in sys.argv:
        kill_server(MONGODB_PORT, "MongoDB server")
    
    print("\n" + "="*50)
    print("Start servers manually with these commands:")
    print("="*50)
    print("\nAPI Server:")
    print(f"cd src/api && uvicorn main:app --reload --port {API_PORT}")
    
    print("\nFrontend Server:")
    print(f"cd src/frontend && npm run dev")
    
    print("\nAccess URLs:")
    print(f"API Documentation: http://localhost:{API_PORT}/docs")
    print(f"Frontend: http://localhost:{FRONTEND_PORT}")


if __name__ == "__main__":
    main()
