import sys
import os

# Add the parent root directory to system paths to resolve main.py imports on container spinup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
