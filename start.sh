#!/bin/bash

mkdir -p /var/log/cron
touch /var/log/cron/cron.log

# Start the cron service
/usr/sbin/cron >> /var/log/cron/cron.log 2>&1

# Add timestamp to log file
echo "Container started at $(date)" >> /var/log/cron/cron.log

cd /app && python trmnl_agenda/main.py >> /var/log/cron/cron.log 2>&1

# Keep the container running by tailing the log file
tail -f /var/log/cron/cron.log