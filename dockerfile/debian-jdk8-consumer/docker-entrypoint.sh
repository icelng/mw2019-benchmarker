#!/bin/bash

set -x

echo "Starting gateway ..."
java -Xms4G \
     -Xmx4G \
     -Dsalt=$2 \
     -Dlogs.dir=/root/runtime/logs \
     -jar \
     -Dloader.path=/root/dists \
     /root/dists/service-consumer.jar > /root/runtime/logs/stdout.log 2>&1
