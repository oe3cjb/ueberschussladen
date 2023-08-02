#!/bin/bash
var=$(date)
if pgrep -af python | grep ueberschuss >/dev/null
then
  echo "$var: Ueberschuss laeuft"
else
  echo "$var: Ueberschuss laeuft NICHT -> Restart"
  nohup python3 -u /home/pi/ueberschussladen/ueberschuss.py > /home/pi/output.log &
fi
