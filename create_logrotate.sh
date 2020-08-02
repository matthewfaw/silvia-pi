#!/bin/bash

logrotate_filename=$1
from_script_or_log=$2

if [ -f $logrotate_filename ]; then
echo "Deleting old logrotate"
rm $logrotate_filename
fi

echo "Create logrotate config from ${from_script_or_log}..."
counter=0
if [[ "$from_script_or_log" == "log" ]]; then
    lognames=$(ls *.log)
elif [[ "$from_script_or_log" == "script" ]]; then
    lognames=$(grep --exclude-dir={www,ivPID,media} --exclude={create_logrotate*,.gitignore,*.out} -rohI "[a-z\-]*\.log")
fi

for logname in $lognames; do
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
