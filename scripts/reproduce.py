"""Run from any working directory: python /path/to/scripts/reproduce.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from movie_analysis.analysis import main

if __name__ == '__main__':
    main()
