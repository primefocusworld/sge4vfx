#!/bin/sh

HOSTNAME=`hostname`

while [ 1 ]; do
	XLOGIN=1
	! w | grep -q '  :[0-9]'  && XLOGIN=0

	# wait for an input
	read input

	if [ "$input" = "quit" ]; then
		exit
	fi

	# echo begin load sensor output
	echo "begin"

	echo "$HOSTNAME:xlogin:$XLOGIN"

	echo "end"
done
