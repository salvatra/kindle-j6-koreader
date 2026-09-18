# Contributing

Keep the Bluetooth host and existing mapper unless a measured defect justifies a
smaller targeted change. This project supports one observed J6/PW5 combination; a
different remote report must include sanitized capabilities and actual behavior.

Before proposing a change, run:

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_repo.py
python3 tools/reproduce.py
```

Tests and CI never need a Kindle, pairing keys, root, or an input-device grab. Add
regressions for observed bugs. For patch edits, update its checksum and provenance,
retain the pinned base commit, and explain changes from the hardware-tested patch.

For hardware reports, include firmware/KOReader/KHP/mapper versions, remote model/mode,
the action performed, expected versus observed result, and whether it was offline.
Remove identifiers and book details. A successful HTTP request is not a physical page
test, a sleep screen is not suspend proof, and unchanged battery percentage is not zero
drain. Separate source observations, mock tests, and physical observations.

Do not upload unredacted diagnostic logs, SSH material, Bluetooth bonds, full databases,
backups or book collections. Keep local captures under ignored `private/`. Changes to
the exact release baseline should include recovery, compatibility and rollback notes.

Keep the publication allowlist in `PUBLIC_FILES.txt` up to date. Downloads and build
outputs belong in ignored `.cache/` and `build/`; device credentials stay outside the
checkout. Keep software test results separate from physical-device observations.

Changes submitted here are under GPL-3.0-or-later unless clearly identified third-party
material carries its own compatible notice. Preserve upstream attribution and licenses.
