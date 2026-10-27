# About this fork

This fork of boltgolt/howdy carries changes that are not in upstream:

- Security hardening: face model files stored root-only instead of
  world-readable, howdy-gtk helper commands run as argv lists instead
  of pkexec shell strings, the PAM compare process spawned with a
  minimal fixed environment, the model download pinned, snapshot
  files created root-only, and code fallbacks aligned with the
  shipped configuration.
- Two runtime fixes: a crash in the end-of-scan report when it
  indexes the winning encoding, and a lid-state glob error logged
  at every authentication on machines without a lid.

Upstream is unmaintained (its last release is from 2020). The
openSUSE package builds from the upstream sources and applies
these changes as patches:
https://build.opensuse.org/package/show/home:scarabeus_iv:howdy
