#!/bin/bash

location=$1

# Remove all empty files
find $location -size 0 -print -delete

echo "DONE! All empty files in $location removed"
