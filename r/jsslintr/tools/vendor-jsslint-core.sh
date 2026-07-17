#!/usr/bin/env bash
# Refreshes the vendored copy of jsslint-core (and the rule-catalogue data
# its build.rs reads) that ships inside this R package.
#
# jsslintr can't depend on ../../../../rust/jsslint-core the way the other
# spec-018 bindings (cli/wasm/py) depend on it as a Cargo workspace member:
# `R CMD build` only tars up files under r/jsslintr, so anything the Rust
# build needs has to physically live inside this package directory. Run
# this script after changing rust/jsslint-core or specs/003-jss-rule-catalogue
# and commit the result.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pkg_dir="$(cd "$script_dir/.." && pwd)"
repo_root="$(cd "$pkg_dir/../.." && pwd)"

core_src="$repo_root/rust/jsslint-core"
core_dest="$pkg_dir/src/rust/jsslint-core"
catalogue_src="$repo_root/specs/003-jss-rule-catalogue"
# Deliberately NOT src/rust/specs: that would put a directory literally
# named "specs" directly in the Cargo workspace root (src/rust, where
# Cargo.toml lives), which is also the cwd the Rust build's linker step
# runs from. Rtools' relocatable mingw-w64 gcc probes its cwd for a
# "specs" override file at startup; finding a directory there instead of
# a file makes it fail with "cannot read spec file './specs': Permission
# denied" on Windows (win-builder). One extra level of nesting keeps
# find_repo_root()'s `specs/003-jss-rule-catalogue/...` marker intact
# while keeping src/rust itself free of a literal "specs" entry.
catalogue_dest="$pkg_dir/src/specs/003-jss-rule-catalogue"

rm -rf "$core_dest"
mkdir -p "$core_dest"
cp "$core_src/build.rs" "$core_dest/"
cp -R "$core_src/src" "$core_dest/src"

# jsslint-core's checked-in Cargo.toml inherits package fields and pinned
# dependency versions from rust/Cargo.toml's [workspace.package] /
# [workspace.dependencies] (it's normally a workspace member). Vendored
# here, it's standalone, so those `.workspace = true` references are
# resolved to literal values pulled from rust/Cargo.toml. It becomes a
# regular (unlisted) member of the jsslintr crate's own single-crate
# "workspace" (jsslintr/src/rust/Cargo.toml's empty [workspace] table) —
# it must NOT declare its own [workspace] table, since a workspace root
# can't contain another workspace root in its directory tree.
sed \
  -e 's/^version\.workspace = true$/version = "1.0.0"/' \
  -e 's/^edition\.workspace = true$/edition = "2021"/' \
  -e 's/^license\.workspace = true$/license = "MIT"/' \
  -e 's/^authors\.workspace = true$/authors = ["Manuel Koller"]/' \
  -e 's/^repository\.workspace = true$/repository = "https:\/\/github.com\/kollerma\/jss-style-checker"/' \
  -e 's/^serde = { workspace = true }$/serde = { version = "1", features = ["derive"] }/' \
  -e 's/^serde_json = { workspace = true }$/serde_json = { version = "1", features = ["preserve_order"] }/' \
  -e 's/^difflib = { workspace = true }$/difflib = "0.4"/' \
  -e 's/^toml = { workspace = true }$/toml = "1"/' \
  "$core_src/Cargo.toml" > "$core_dest/Cargo.toml"

rm -rf "$catalogue_dest"
mkdir -p "$catalogue_dest"
cp "$catalogue_src/catalogue.yaml" "$catalogue_src/terms.json" "$catalogue_src/latex-macro-specs.json" "$catalogue_dest/"

echo "Vendored jsslint-core -> $core_dest"
echo "Vendored catalogue data -> $catalogue_dest"
