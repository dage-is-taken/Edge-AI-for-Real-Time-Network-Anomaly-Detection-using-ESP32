#!/bin/bash

TARGET="192.168.1.126"

while true
do
    nmap -sS $TARGET >/dev/null 2>&1
    sleep 1
done