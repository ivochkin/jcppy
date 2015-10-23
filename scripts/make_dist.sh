#!/usr/bin/env bash
root=$(pwd -P)
version=$(git describe --tags)

files=__main__.py
files="$files $(find jcppy -name '*.py')"

for i in $files;
do
  if [ ! -f $i ]
  then
    echo "file $i is missing" && exit 1
  fi
done

$root/scripts/check_sources_header.sh || exit 1

mkdir -p $root/dist
zip $root/dist/jcppy-$version.py.zip $files
