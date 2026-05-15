#!/bin/bash
# CardNews Editor — Mac 실행 스크립트
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip -q
    .venv/bin/pip install PyQt6 Pillow pandas openpyxl -q
    echo "설치 완료"
fi

.venv/bin/python3 main.py
