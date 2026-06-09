# Breaking-change patterns by ecosystem

What to look for in changelogs/migration guides, and how it manifests.

## Universal signals in release notes
- Sections titled "Breaking changes", "Migration", "Upgrade guide", "Removed".
- A bumped **major** version, or any change to a `0.x` library's **minor**.
- Raised minimum runtime (Node 18→20, Python 3.8→3.10, Go 1.21→1.22, edition).
- Changed peer-dependency ranges (your other packages may need to move too).
- Renamed/removed exports, changed default options, config-schema changes.

## Node / npm
- **ESM vs CJS**: a package shipping ESM-only (no `require`) breaks CJS
  consumers. Symptoms: `ERR_REQUIRE_ESM`, `Cannot use import statement`.
  Fix: move to dynamic `import()`, or set `"type": "module"`, or stay on the
  last CJS-compatible version.
- **Peer dependency conflicts**: `npm install` warns/errs `ERESOLVE`. Resolve
  the peer (e.g. bump the framework) rather than `--force`/`--legacy-peer-deps`
  unless intentional and documented.
- **`engines` bump**: build fails on CI with an older Node. Bump the runtime in
  CI/Docker too.
- **Type-only packages** (`@types/*`): must track the runtime lib's major.
- **Removed deep imports**: `require('pkg/lib/internal')` paths often vanish;
  use the public entrypoint or `exports` map.

## Python
- **Removed/renamed APIs**: e.g. SQLAlchemy 1.x→2.0 query API, Pydantic 1→2
  (`BaseSettings` moved to `pydantic-settings`, validator decorators renamed).
- **Type-stub mismatches**: mypy/pyright start failing though runtime is fine.
- **Dropped Python versions**: `requires-python` raised; your CI matrix breaks.
- **C-extension / wheel** availability for your platform/arch (numpy, pillow).

## Rust
- **Edition bumps** (2018→2021→2024) may require source changes; controlled by
  `edition` in `Cargo.toml`, independent of dep versions.
- **MSRV** (minimum supported Rust version) raised — toolchain must move.
- **Feature-flag renames** and default-feature changes.
- Re-exported types changing path; trait method signature changes.

## Go
- **Major version = new import path** (`/v2` suffix). `go get foo@v2.0.0` is not
  enough; import paths in code must change to `foo/v2`.
- Removed/renamed exported identifiers (caught at build time — good).
- `go.mod` `go 1.xx` directive raising the language version.

## Java
- `javax.*` → `jakarta.*` namespace migration (Spring Boot 3, Jakarta EE 9+).
- Removed deprecated methods; changed default configuration properties.

## How to detect impact fast
1. Read the migration guide; list each breaking item.
2. `grep`/search the codebase for the affected symbol or import.
3. For type-checked languages, lean on the compiler/type-checker as the
   detector after the bump.
4. Run the test suite — but remember tests may not cover every call site.
5. For frameworks, run a smoke test / start the app, not just unit tests.
