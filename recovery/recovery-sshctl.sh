#!/bin/sh
# On-demand recovery shell. No boot hooks, USB-mode changes or power settings.
set -eu
# Library contains only pure validation functions; --check-config never changes the host.
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "$HERE/config.sh"
case "${1-}" in
    --help|-h) echo 'Usage: recovery-sshctl.sh start|stop|--check-config FILE'; exit 0;;
    --check-config)
        [ "$#" = 2 ] || exit 2
        validate_client_file "$2" || { echo 'Invalid client IPv4 configuration.' >&2; exit 2; }
        echo 'Valid single private IPv4 client.'; exit 0;;
    start|stop) [ "$#" = 1 ] || exit 2;;
    *) echo 'Use start, stop or --check-config FILE.' >&2; exit 2;;
esac
umask 077
BASE=/mnt/us/kindle-remote-recovery
PIDFILE=/tmp/kindle_remote_recovery.pid
LOCK=/tmp/kindle_remote_recovery.lock
PORT=2223
[ "$(id -u)" = 0 ] || exit 2
[ -d "$BASE" ] && [ ! -L "$BASE" ] || exit 2
validate_client_file "$BASE/allowed_client_ipv4" || { echo 'Invalid client IPv4 configuration.'; exit 2; }
CLIENT=$(cat "$BASE/allowed_client_ipv4")

rule() {
    direction=$1
    operation=$2
    case "$direction" in
        INPUT) iptables "$operation" INPUT -i wlan0 -s "$CLIENT" -p tcp --dport "$PORT" -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT ;;
        OUTPUT) iptables "$operation" OUTPUT -o wlan0 -d "$CLIENT" -p tcp --sport "$PORT" -m conntrack --ctstate ESTABLISHED -j ACCEPT ;;
        *) exit 2 ;;
    esac
}

owned_pid() {
    case "$1" in ''|*[!0-9]*) return 1;; esac
    [ "$(readlink "/proc/$1/exe" 2>/dev/null)" = "$BASE/dropbear" ]
}

mkdir "$LOCK" || { echo 'Recovery control is already running; no second operation.'; exit 1; }
trap 'rmdir "$LOCK" 2>/dev/null || :' EXIT
trap 'exit 1' HUP INT TERM

case "${1-}" in
    start)
        if [ -f "$PIDFILE" ]; then
            pid=$(cat "$PIDFILE")
            if owned_pid "$pid"; then echo 'Recovery SSH is already running.'; exit 0; fi
            case "$pid" in ''|*[!0-9]*) exit 2;; esac
            [ ! -d "/proc/$pid" ] || { echo 'PID belongs to another process; stopping.'; exit 2; }
            rm "$PIDFILE"
        fi
        ip=$(ifconfig wlan0 | sed -n 's/.*inet addr:\([0-9.]*\).*/\1/p')
        valid_private_ipv4 "$ip" || { echo 'Connect to the configured private Wi-Fi network first.'; exit 2; }
        cd "$BASE"
        sha256sum -c runtime.sha256 >/dev/null || { echo 'Recovery files changed; refusing start.'; exit 2; }
        [ -s settings/SSH/authorized_keys ] && [ -s settings/SSH/host_ed25519 ]
        # Refuse unexpected preexisting exact rules rather than claiming ownership.
        if rule INPUT -C 2>/dev/null || rule OUTPUT -C 2>/dev/null; then
            echo 'Recovery firewall rule already exists; inspect before restarting.'
            exit 2
        fi
        input_added=0
        output_added=0
        cleanup_failed_start() {
            for entry in /proc/[0-9]*/exe; do
                path=$(readlink "$entry" 2>/dev/null) || continue
                [ "$path" = "$BASE/dropbear" ] || continue
                pid=${entry#/proc/}; pid=${pid%/exe}
                owned_pid "$pid" && kill -TERM "$pid" 2>/dev/null || :
            done
            [ "$output_added" = 0 ] || rule OUTPUT -D 2>/dev/null || :
            [ "$input_added" = 0 ] || rule INPUT -D 2>/dev/null || :
            rmdir "$LOCK" 2>/dev/null || :
        }
        trap cleanup_failed_start EXIT
        rule INPUT -I
        input_added=1
        rule OUTPUT -I
        output_added=1
        # Empty environment avoids inheriting KOReader library paths or preload hooks.
        env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin LD_LIBRARY_PATH="$BASE/libs" \
            /usr/bin/setsid "$BASE/dropbear" -E -s -j -k -I 300 \
            -D "$BASE/settings/SSH" -r "$BASE/settings/SSH/host_ed25519" \
            -p "$ip:$PORT" -P "$PIDFILE" </dev/null >>"$BASE/recovery-ssh.log" 2>&1
        count=0
        while [ "$count" -lt 3 ]; do
            if [ -f "$PIDFILE" ] && owned_pid "$(cat "$PIDFILE")"; then
                trap 'rmdir "$LOCK" 2>/dev/null || :' EXIT
                echo "Recovery SSH started on $ip:$PORT (keys only; client $CLIENT)."
                exit 0
            fi
            sleep 1
            count=$((count + 1))
        done
        echo 'Recovery SSH did not start; firewall additions removed.'
        exit 1
        ;;
    stop)
        # Match only this copied executable, including its own session children.
        for entry in /proc/[0-9]*/exe; do
            path=$(readlink "$entry" 2>/dev/null) || continue
            [ "$path" = "$BASE/dropbear" ] || continue
            pid=${entry#/proc/}; pid=${pid%/exe}
            owned_pid "$pid" && kill -TERM "$pid" 2>/dev/null || :
        done
        for direction in INPUT OUTPUT; do
            if rule "$direction" -C 2>/dev/null; then rule "$direction" -D; fi
        done
        sleep 1
        for entry in /proc/[0-9]*/exe; do
            path=$(readlink "$entry" 2>/dev/null) || continue
            [ "$path" != "$BASE/dropbear" ] || { echo 'A recovery process remains; inspect before cleanup.'; exit 1; }
        done
        [ ! -f "$PIDFILE" ] || rm "$PIDFILE"
        echo 'Recovery SSH stopped; its firewall rules removed.'
        ;;
    *) echo 'Use start or stop.'; exit 2;;
esac
