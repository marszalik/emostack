#!/bin/bash
cd /home/eli/dev/emostack3
echo "$(date) koder"; timeout 900 gpu koder 2>&1 | tail -2
.venv/bin/python data/nmi/code_arms.py 8 wound=73:38:C,E,W:1,14,16 sceptic=74:39:C,E,W:2,15,3,4,5
echo "$(date) tekst"; timeout 900 gpu tekst 2>&1 | tail -2
echo "$(date) session done"
