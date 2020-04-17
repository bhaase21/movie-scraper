#!/bin/sh

python app.py --trailerfind yes
#python app.py --recent yes --daysback 7 --daysforward 365
python app.py --recent yes --daysforward 90
python app.py --tvpopular yes
