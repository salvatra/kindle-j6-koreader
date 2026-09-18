#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Pure validation: one canonical RFC1918 IPv4 address, never a subnet/shell fragment.
valid_private_ipv4() {
    [ "$#" = 1 ] || return 1
    printf '%s\n' "$1" | awk -F. '
        NR != 1 { bad=1 }
        NF != 4 { bad=1 }
        {
            for (i=1; i<=NF; i++) {
                if ($i !~ /^[0-9]+$/ || length($i)>3 || $i>255 ||
                    (length($i)>1 && substr($i,1,1)=="0")) bad=1
            }
            if (!($1==10 || ($1==172 && $2>=16 && $2<=31) ||
                  ($1==192 && $2==168))) bad=1
        }
        END { exit (NR!=1 || bad) ? 1 : 0 }
    '
}

validate_client_file() {
    [ "$#" = 1 ] && [ -f "$1" ] && [ ! -L "$1" ] || return 1
    # Exactly one line, with one terminating newline, rejects ambiguous records.
    [ "$(wc -l < "$1" | tr -d ' ')" = 1 ] || return 1
    [ "$(wc -c < "$1" | tr -d ' ')" -le 16 ] || return 1
    client_value=$(cat "$1")
    valid_private_ipv4 "$client_value"
}
