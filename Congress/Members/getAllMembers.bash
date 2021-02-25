#!/bin/bash
for session in {71..117}
do
python memberCollector.py -s $session -c House
python memberCollector.py -s $session -c Senate
done
exit 0
