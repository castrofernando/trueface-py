# !/usr/bin/env bash

echo "Start trueface script"
cd -- "/home/pi/trueface-py"

sudo nohup python3 -u main.py > cmd.log & 
