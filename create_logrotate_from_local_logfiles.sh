#!/bin/bash

logrotate_filename=$1

if [ -f $logrotate_filename ]; then
echo "Deleting old logrotate"
rm $logrotate_filename
fi

echo "Create logrotate config..."
counter=0
for logname in `ls *.log`; do
if [ $counter -eq 0 ]; then
counter=1
else
echo "" >> ${logrotate_filename}
fi
echo "$(pwd)/${logname} {
  rotate 7
  daily
  compress
  copytruncate
  missingok
  notifempty
}" >> ${logrotate_filename}
done
