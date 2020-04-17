#!/bin/sh
ids='ids.txt' #zcat movie_ids_04_13_2020.json.gz | jq '.id'`

i=1
while read id; do
  echo line: $i
  python3.6 app.py --update yes --movieid  $id

  i=`expr $i + 1`

done <$ids
