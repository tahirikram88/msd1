#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install pytest boto3 botocore requests

echo "Demo environment bootstrapped."
echo "Run unit tests from case-study-2 with: python3 -m pytest -q"
