#!/bin/bash
# place this in the folder with the thread json files, along with the get_messages.py script

OIFS="$IFS"
IFS=$'\n'
for thread_file in $(ls *.json); do
    ./get_messages.py --from-file "$thread_file" > "${thread_file}.txt"
done
IFS="$OIFS"
