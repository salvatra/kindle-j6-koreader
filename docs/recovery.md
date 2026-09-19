# Optional recovery shell

The reference setup used a copied, compatible Dropbear binary and library outside the
KOReader directory, with Start/Stop scriptlets in the native library. Authentication,
stop/restart cleanup and access with KOReader closed were tested. This is recovery from
application/plugin failure **while the OS and Wi-Fi work**, not failed-boot recovery.

The public controller additionally accepts a validated, configurable single RFC1918
client address. This generalization is covered by host mocks, **not a new on-device
test**. It has not replaced the controller on the reference Kindle. Independent
key-only access was verified again at final cleanup on 19 September, then both SSH
servers and their exact temporary firewall rules were closed. The recovery files and
shortcuts remain available on demand. There are no binaries or credentials in this
repository. [Final setup record](final-record.md).

## Prepare on the development host

Use an existing independently tested recovery solution if you have one. Otherwise first
establish temporary, key-only KOReader SSH or another authenticated setup channel and
verify its host fingerprint. Do not enable passwordless root login or disable host-key
checking. The router's default-gateway address is not the Kindle's IPv4 address.

Keep all key material outside the checkout, for example a private directory under your
user data directory, mode 0700. Generate a dedicated client login key with `ssh-keygen`;
copy only its `.pub` contents into the staged server `settings/SSH/authorized_keys`.
Generate a **distinct server key in Dropbear format**, using compatible `dropbearkey`
or `dropbearconvert` tooling, and record its public fingerprint. Do not assume an OpenSSH
private-key file can be copied directly into every Dropbear build. With those optional
host tools already available, example key-generation commands in the private directory:

```sh
ssh-keygen -t ed25519 -f identity_ed25519 -C kindle-maintenance
dropbearkey -t ed25519 -f recovery_host_ed25519
dropbearkey -y -f recovery_host_ed25519
```

Choose a passphrase for the client key as appropriate for your SSH client. The server
key must be usable noninteractively by the on-demand server. Retain its public key for
an explicit pinned known-hosts entry. Never print or commit private-key contents.

Find the actual client IPv4 selected by the route to your Kindle. Write **one address
and one newline** to a private `allowed_client_ipv4` file; no subnet, list or shell code.
Check the file before transferring:

```sh
sh recovery/recovery-sshctl.sh --check-config /path/to/private/allowed_client_ipv4
```

The example `10.23.45.67` is a dummy, not a discovered device. DHCP can change your
computer's address; stop recovery before updating the allowance and its manifest. This
single-client restriction intentionally does not silently widen to the whole LAN.
The controller adds two narrow ACCEPT rules to the existing Kindle firewall; it does
not replace its policy. Before starting, verify that the existing policy blocks other
clients on this port and that no broader ACCEPT rule bypasses the restriction. The
helper alone cannot promise single-client access on an arbitrary permissive firewall.

## Assemble on Kindle through the setup channel

Before writing, confirm every destination is absent or belongs to your recorded setup;
back up existing files and stop conflicting listeners. Prepare this layout under
`/mnt/us/kindle-remote-recovery` (private directory permissions, files readable by root):

```text
dropbear                         copied from the compatible existing KOReader install
libs/libz.so.1                   its verified compatible library
recovery-sshctl.sh               from this repository
config.sh                       pure address-validation functions from this repository
Start-Remote-Recovery.sh         from this repository
Stop-Remote-Recovery.sh          from this repository
allowed_client_ipv4             your private single-client configuration
settings/SSH/authorized_keys     dedicated client PUBLIC key only
settings/SSH/host_ed25519        dedicated Dropbear SERVER private key
runtime.sha256                  generated locally after staging
```

The reference copied KOReader's Dropbear v2026.92 and `libs/libz.so.1` on the tested PW5.
Inspect your actual binary's ABI, dependencies and supported `-D`, `-r`, `-p`, `-s`,
`-j`, `-k`, `-I` flags first. The controller uses a clean environment and its own library
path. A different KOReader build may require a different dependency bundle: stop rather
than assuming this single library is universal.

Set executable mode 0700 for the copied server and scripts; keep keys/config files 0600.
Generate the local manifest **from within that directory**, including the controller,
validation library, copied runtime and key files:

```sh
sha256sum dropbear libs/libz.so.1 recovery-sshctl.sh config.sh \
  Start-Remote-Recovery.sh Stop-Remote-Recovery.sh allowed_client_ipv4 \
  settings/SSH/authorized_keys settings/SSH/host_ed25519 > runtime.sha256
sha256sum -c runtime.sha256
```

This installed manifest is private/local and is not the public source manifest. It
detects unexpected local changes; it is not a signature against a compromised root OS.
Copy only the two launchers into `/mnt/us/documents/`, retaining their filenames and
making them executable for the existing scriptlet workflow. Do not modify app databases,
install KUAL or add boot hooks just to launch recovery.

## Prove it before system installation

1. With setup access still available, open **Start Remote Recovery** from the native
   library. The launcher runs the controller under a 15-second bound.
2. Verify a listener on the Kindle's actual WLAN IPv4, port 2223, and the two exact firewall
   rules limited to your client address. It uses key-only auth, disables forwarding and
   has a 300-second idle-session timeout. It does not set sleep inhibitors.
3. Authenticate using your dedicated client key and the distinct pinned server public
   key. Use one bounded read-only command; do not accept an unexpected host identity.
4. Use **Stop Remote Recovery** through the native launcher or the separate setup channel.
   Check that only its copied executable and exact rules were removed; test start again.
5. Fully exit KOReader and close its setup SSH. Authenticate to recovery again and confirm
   KOReader is absent. Keep recovery available during the later system change.

A representative client command, after creating the pinned known-hosts entry from the
verified server public key, is:

```sh
ssh -F /dev/null -p 2223 -i /path/to/private/identity_ed25519 \
  -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes \
  -o UserKnownHostsFile=/path/to/private/known_hosts-recovery \
  -o ClearAllForwardings=yes -o ConnectTimeout=5 -o ConnectionAttempts=1 \
  root@KINDLE_IPV4 'timeout -s KILL 10 /bin/sh -c "id -u; uname -r"'
```

Replace paths and address; the placeholder is deliberately not executable unchanged.
Stopping recovery through the recovery session itself terminates that session. Do not
use `killall dropbear`: it can terminate a different recovery/setup endpoint. On the
tested KOReader version, its force-close option could affect other Dropbear processes;
the project therefore used identity-checked maintenance cleanup instead.

## Bounds and rollback

Start refuses unexpected PID ownership, stale owned rules, invalid client addresses or
manifest failures. Stop matches only the copied executable and removes only its exact
client/port rules. No permanent service, root remount, network scan or radio takeover is
introduced. The client allowance and listener bind are independent; update both evidence
records when DHCP changes.

To remove this optional setup, first prove stop cleanup, then remove only manifest-known
files and the two matching launcher copies. Preserve unexpected files; remove directories
only when empty. Do not remove keys/backups until you have an adequate alternate recovery
path. Close recovery, setup SSH and Wi-Fi during battery observations.
