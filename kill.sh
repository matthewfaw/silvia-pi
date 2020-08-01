#!/bin/bash

ps -ef | grep "^root.*python" | sed 's/  */ /g' | cut -f2 -d' ' | while read f; do sudo kill -9 $f; done
