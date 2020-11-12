#!/bin/bash

# if backup same as new delete it
if cmp -s dbase/lg.sqlite dbase/lg.sqlite.bak
then
   rm dbase/lg.sqlite.bak
else
   d=$(date "+%F-%H-%M-%S")
   mv -f dbase/lg.sqlite.bak dbase/lg.sqlite.$d
fi

# delete backups older than a week
find dbase/lg.sqlite.2* -mtime +7 -delete &>/dev/null

