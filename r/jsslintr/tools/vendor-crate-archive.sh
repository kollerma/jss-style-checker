#!/usr/bin/env bash
# Refreshes everything CRAN's offline-install requirement needs:
#
#   1. Regenerates R/extendr-wrappers.R from the compiled library's own
#      extendr metadata (`cargo run --bin document`), so the committed
#      wrapper file can't drift from the `#[extendr]` function signatures.
#      This step needs the network (ordinary, non---offline cargo) — it's
#      a dev-time step, never run at install time (see src/Makevars,
#      which ships the wrappers pre-generated instead of regenerating
#      them). check-standard.yaml re-runs this same step in CI and diffs
#      the result, so a forgotten refresh fails loudly instead of quietly
#      shipping stale wrappers.
#   2. Runs `cargo vendor` over src/rust's dependency graph and archives
#      the result as src/rust/vendor.tar.xz, plus the matching
#      src/rust/vendor-config.toml source-replacement config — what
#      Makevars/Makevars.win extract and point CARGO_HOME at so
#      `cargo build --offline` never touches the network or ~/.cargo.
#      Named without a leading dot (unlike a real .cargo/config.toml) so
#      it doesn't trip R CMD check's "hidden files and directories" NOTE
#      when it ships in the tarball; Makevars copies it into a real
#      .cargo/config.toml under an ephemeral, install-time-only CARGO_HOME.
#
# Run this after changing src/rust/Cargo.toml, its Cargo.lock, or the
# `#[extendr]` function surface, and commit the result (R/extendr-wrappers.R,
# src/rust/vendor.tar.xz, src/rust/vendor-config.toml). It's also invoked
# automatically at the end of vendor-jsslint-core.sh, since bumping the
# vendored jsslint-core copy is the most common reason the lock changes.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pkg_dir="$(cd "$script_dir/.." && pwd)"
src_dir="$pkg_dir/src"
rust_dir="$src_dir/rust"

echo "==> Regenerating R/extendr-wrappers.R"
(
  cd "$src_dir"
  cargo run --bin document --release --locked \
    --manifest-path=./rust/Cargo.toml --target-dir ./rust/target
)

echo "==> Vendoring src/rust dependency graph"
rm -rf "$rust_dir/vendor" "$rust_dir/vendor-config.toml"
(
  cd "$rust_dir"
  cargo vendor --locked vendor > vendor-config.toml
)

echo "==> Archiving vendor/ -> src/rust/vendor.tar.xz"
(
  cd "$rust_dir"
  tar -cJ --no-xattrs -f vendor.tar.xz vendor
  rm -rf vendor
)

echo "Wrote $rust_dir/vendor.tar.xz"
echo "Wrote $rust_dir/vendor-config.toml"
echo "Refreshed $pkg_dir/R/extendr-wrappers.R"
