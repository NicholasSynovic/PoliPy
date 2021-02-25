#!/bin/bash
for session in {71..117}
do
python treatyDocumentsCollector.py -s $session -c House
python treatyDocumentsCollector.py -s $session -c Senate
done
exit 0
