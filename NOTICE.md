# Attribution and license boundaries

This repository's original code and documentation are distributed under
**GPL-3.0-or-later**, except where another original notice explicitly applies. See
[LICENSE](LICENSE). Project documentation and companion tooling: salvatra, 2026.

The mapper patch is a modification of **Kindle Button Mapper** by Lucas Zampieri and
its contributors. Its pinned [Cargo metadata](https://github.com/zampierilucas/kindle-button-mapper-rs/blob/fa3a851ef1d26f3045ef27c7dc3465e45d56de14/Cargo.toml)
declares GPL-3.0-or-later. Preserve upstream notices and license files when applying or
redistributing the patched source. Do not attribute the complete mapper to this project.

**Kindle HID Passthrough**, its runtime and its bundled KOReader integration remain
upstream work by Lucas Zampieri and contributors. [Pinned license](https://github.com/zampierilucas/kindle-hid-passthrough/blob/v3.16.0/LICENSE).
**KOReader** remains the work of its upstream contributors; [upstream project](https://github.com/koreader/koreader).

Dropbear, Rust/Cargo, their libraries, and Rust dependencies retain their own licenses.
They are fetched or reused separately, not relicensed by this repository. The optional
recovery controller reuses a compatible existing Dropbear binary; no Dropbear binary or
private key is included. No Amazon firmware, manufacturer manual scan, book, or complete
third-party release is redistributed here.

The gesture fixture is a sanitized numeric projection of six project-recorded Arch
events. It is not a Kindle event recording. Its device identifier is synthetic; the
gesture coordinates and templates are preserved. See [provenance](provenance/sources.json).
