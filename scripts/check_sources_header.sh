#!/usr/bin/env bash
root=$(pwd -P)
ret=0

function report {
  echo Bad header in file $1, line $2
  ret=1
}

header=(
  '#!/usr/bin/env python'
  '# -*- coding: utf-8 -*-'
  '# Copyright (c) 2015 Stanislav Ivochkin <isn@extrn.org>'
  '# License: MIT (see LICENSE for details)'
)

for file in $(find $root -name '*.py'); do
  echo "checking header in $file"
  for i in ${!header[*]}; do
    [ "$(cat $file | sed -n $((i+1))p)" == "${header[$i]}" ] || report $file $((i+1))
  done
done

exit $ret
