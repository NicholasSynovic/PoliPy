#!/bin/bash
for session in {71..117}
do
python legislationCollector.py -s $session
done
exit 0
