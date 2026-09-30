@echo off
echo ======================================================================
echo Starting WeighProof: OIML R 76 NAWI Test Report Generator (SIH 2026)
echo ======================================================================
cd /d %~dp0
set PYTHONPATH=%~dp0backend
echo Starting full-stack server on http://localhost:8000 ...
python backend\main.py
