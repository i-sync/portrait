#! /bin/bash

cd /var/www/portrait/xiuren

ts=`date +%s`

nohup /usr/local/bin/scrapy crawl album > "nohup-$ts.out" 2>&1 &

echo "sleep 180, and then regenerate sitemap."
sleep 180

/usr/bin/python3 /var/www/portrait/tools/generate-sitemap.py