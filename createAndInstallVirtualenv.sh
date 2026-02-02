#!/usr/bin/env bash
PYTHON=python3.11
$PYTHON -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\Activate.ps1

pip install -e .
