#!/bin/bash
#copy from shadowsocksR/run.sh
cd "$(dirname "$0")"
python_ver='python2.7'
eval $(ps -ef | grep "[0-9] ${python_ver} ddns-aliyun\\.py" | awk '{print "kill "$2}')
