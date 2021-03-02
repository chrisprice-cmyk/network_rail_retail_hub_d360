#!/bin/bash
# loops through each git submodule found under lib and asks if you want to update individual ones
subModRootDir="lib"


for d in $(find $subModRootDir -maxdepth 1 -type d)
do
  #Do something, the directory is accessible with $d:
  if [[ "$d" == *\/* ]]; then
    read -p 'Update submodule '$d' (y/n): ' yesNo
    if [ $yesNo == 'y' ]; then
      git submodule update --remote $d
    fi
  fi
done
