#!/bin/sh
# three more background lives (variant C), one after another; Eliza, 26 October night
cd /home/eli/dev/emostack3
for n in 4 5 6; do .venv/bin/python data/dayBackground/live_c.py 9 C > data/dayBackground/live_c$n.log 2>&1; done
