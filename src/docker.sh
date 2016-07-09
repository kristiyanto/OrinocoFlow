#!/bin/bash
cd /data
for f in *.txt
do
	echo "Trying: $f"
	python /insight/src/rolling_median.py "$f" "OUT_$f"
	echo "_______"
	if ! [ -s "OUT_$f" ]; then
		rm "OUT_$f"
	fi
done