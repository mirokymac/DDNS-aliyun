#!/bin/bash
#copy from shadowsocksR/run.sh
cd "$(dirname "$0")"
python_ver='python2.7'
is_alive=$(ps -ef | grep "[0-9] ${python_ver} ddns-aliyun\\.py" | awk '{print $2}')
if [ "$is_alive" ]; then
	echo "ddns is alive. pid: ${is_alive}"
else
	nohup ${python_ver} ddns-aliyun.py >> /dev/null &
fi
