#!/usr/bin/env python3
"""
Helper module to handle path resolution for LangRead scripts.
This ensures scripts can be run from any directory and still find their required modules.
"""

import os
import sys

def setup_path():
    """
    Add the project root directory to sys.path.
    This allows scripts to import modules from the src directory regardless of where they're run from.
    """
    # Get the directory where this script is located (should be 'scripts/')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get the project root (parent directory of 'scripts/')
    project_root = os.path.dirname(script_dir)
    
    # Add project root to sys.path if it's not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    return project_root
