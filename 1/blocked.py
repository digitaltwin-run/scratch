#!/usr/bin/env python3
"""
Blockly YAML Editor
Edytor plików YAML (docker-compose, etc.) oraz Dockerfile z interfejsem Blockly
"""

import os
import sys
import json
import yaml
import webbrowser
import threading
import time
import shutil
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import argparse
import signal
import atexit

app = Flask(__name__)
CORS(app)

# [Rest of the Python code from the main artifact goes here]
# For brevity, I'm not repeating the entire code, but it should be copied from the main artifact

