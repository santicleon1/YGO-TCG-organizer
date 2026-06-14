from pathlib import Path
import json

def config():
    # project root
    root = Path(__file__).resolve().parent.parent
    return root / "config.json"


def read_config():
    config_file = config()
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


def write_config(data):
    config_file = config()
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)