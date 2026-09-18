#!/bin/sh
# Name: Stop Remote Recovery
# Author: Local Kindle remote setup
exec timeout -s KILL 15 /bin/sh /mnt/us/kindle-remote-recovery/recovery-sshctl.sh stop
