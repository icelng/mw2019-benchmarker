#!/bin/bash


set -x

if [[ "$1" == "provider-small" ]]; then
  echo "Starting small provider service..."
  java  -Xms1G \
        -Xmx1G \
        -Dsalt=$2 \
        -Dquota=small \
        -Dloader.path=/root/dists \
        -Dlogs.dir=/root/runtime/logs \
         -jar \
        /root/dists/service-provider.jar > /root/runtime/logs/stdout.log 2>&1
elif [[ "$1" == "provider-medium" ]]; then
  echo "Starting medium provider service..."
  java  -Xms2G \
        -Xmx2G \
        -Dsalt=$2 \
        -Dquota=medium \
        -Dlogs.dir=/root/runtime/logs \
        -Dloader.path=/root/dists \
        -jar \
        /root/dists/service-provider.jar > /root/runtime/logs/stdout.log 2>&1
elif [[ "$1" == "provider-large" ]]; then
  echo "Starting large provider service..."
  java  -Xms3G \
        -Xmx3G \
        -Dsalt=$2 \
        -Dquota=large \
        -Dloader.path=/root/dists \
        -Dlogs.dir=/root/runtime/logs \
        -jar \
        /root/dists/service-provider.jar > /root/runtime/logs/stdout.log 2>&1
else
  echo "[ERROR] Unrecognized arguments, exit."
  exit 1
fi
