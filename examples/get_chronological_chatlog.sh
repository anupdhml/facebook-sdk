#!/bin/bash
# place this in the folder with the thread json files, along with the get_messages.py script

fbuserid="$1"

OIFS="$IFS"
IFS=$'\n'
for thread_file in $(ls *.json); do
    ./get_messages.py --from-file "$thread_file" > "${thread_file}.txt"
    #filter by certain user
    #./get_messages.py --from-file "$thread_file" | grep "$fbuserid" | cut -d'|' -f3 | grep -v '(null)' > "${thread_file}.txt"
done
IFS="$OIFS"
