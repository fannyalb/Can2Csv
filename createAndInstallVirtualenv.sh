#!/usr/bin/env bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\Activate.ps1

pip install -e .
