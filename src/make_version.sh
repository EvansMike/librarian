#!/bin/sh
# Update a version header file.


ROOT=$(git rev-parse --show-toplevel)
DATE=$(date +%Y-%m-%d)
#How many commits today?
COMMITS=$(git rev-list HEAD --count --since="00:00" ) 
COMMITS=$(echo "$COMMITS + 1" | bc)
REV=$DATE.$COMMITS
VERSION=$ROOT/src/version.py

# Client
if [ -f $VERSION ]
then
echo "''' Version number by date and daily commits.'''" > $VERSION
echo "__version__ = \"$DATE.$COMMITS\"" >> $VERSION
fi

