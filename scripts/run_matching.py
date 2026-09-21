"""Reproduce the four historical matching rounds in order."""
from pathlib import Path
import subprocess
import sys

if __name__ == '__main__':
    for step in range(1, 5):
        subprocess.run([sys.executable, str(Path(__file__).with_name(f'match_{step:02d}.py'))], check=True)
