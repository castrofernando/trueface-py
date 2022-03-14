# !/usr/bin/env bash

echo "Start trueface script"
cd -- "/home/pi/Downloads/my_detection"

sudo python3 main.py 2>errors.log 1>output.log &
