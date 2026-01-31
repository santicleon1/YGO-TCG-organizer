from pathlib import Path
import json

def config():
    # project root
    root = Path(__file__).resolve().parent.parent
    config_file = root / "config.json"
    
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)
