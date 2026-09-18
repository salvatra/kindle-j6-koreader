#!/bin/sh
# Name: Start Remote Recovery
# Author: Local Kindle remote setup
exec timeout -s KILL 15 /bin/sh /mnt/us/kindle-remote-recovery/recovery-sshctl.sh start
