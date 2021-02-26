#!/bin/bash
for session in {71..117}
do
python treatyDocumentsCollector.py -s $session
done
exit 0
