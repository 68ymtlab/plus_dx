@echo off
title Simple Server
cd %~dp0
start python main.py
timeout 5 > nul
start chrome 127.0.0.1:8000/