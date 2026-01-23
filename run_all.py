# run_all.py
# Ein-Klick-Start fuer die Pipeline
import subprocess
import sys
from pathlib import Path


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    subprocess.run([sys.executable, "-m", "src.run_pipeline"], cwd=str(root), check=True)
