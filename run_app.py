from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
os.chdir(BASE_DIR)

import uvicorn


def main() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8031, reload=False)


if __name__ == "__main__":
    main()
