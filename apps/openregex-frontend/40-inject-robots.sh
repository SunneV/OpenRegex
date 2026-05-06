#!/bin/sh
set -e

ROBOTS_VALUE="${ROBOTS_META:-noindex, nofollow}"
sed -i "s/__ROBOTS_META_PLACEHOLDER__/${ROBOTS_VALUE}/g" /usr/share/nginx/html/index.html