#!/bin/sh
# cf: python sd_processor.py 00100277 cognition sd_test 10 20
# sh start_scrape.sh 00100277 cognition sd_test 10 130

nohup python sd_processor.py $1 $2 $3 $4 $5 $6 &
echo 'Start to scraping websites!'
