import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
service_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(service_dir)
sys.path.insert(0, project_root)
