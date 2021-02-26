#!/bin/bash
for session in {71..117}
do
python legislationCollector.py -s $session -c House
python legislationCollector.py -s $session -c Senate
done
exit 0
