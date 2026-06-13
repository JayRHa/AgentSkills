# Ecosystem command reference

Canonical commands per package manager. Always prefer the project's own
scripts (`package.json` scripts, `Makefile`, `tox.ini`) for the test/build
gate when they exist.

## Detecting the ecosystem

| Manifest present | Ecosystem | Manager(s) |
|------------------|-----------|------------|
| `package.json` + `package-lock.json` | Node | npm |
| `package.json` + `yarn.lock` | Node | yarn |
| `package.json` + `pnpm-lock.yaml` | Node | pnpm |
| `pyproject.toml` (+ `poetry.lock`) | Python | poetry |
| `pyproject.toml` (+ `uv.lock`) | Python | uv |
| `requirements*.txt` | Python | pip |
| `Cargo.toml` + `Cargo.lock` | Rust | cargo |
| `go.mod` + `go.sum` | Go | go |
| `Gemfile` + `Gemfile.lock` | Ruby | bundler |
| `composer.json` + `composer.lock` | PHP | composer |
| `pom.xml` | Java | maven |
| `build.gradle(.kts)` | Java/Kotlin | gradle |

## npm
```sh
npm outdated                      # list outdated (table)
npm outdated --json               # machine-readable
npm audit                         # advisories
npm audit fix                     # auto-fix non-breaking
npm install <pkg>@<version>       # bump one package, updates lockfile
npm update                        # apply in-range updates (patch/minor)
npm test                          # gate (or the project's test script)
npm ci                            # clean install from lockfile (rollback check)
```

## yarn (classic / berry)
```sh
yarn outdated
yarn npm audit                    # berry; classic: yarn audit
yarn up <pkg>@<version>           # berry; classic: yarn upgrade <pkg>@<v>
yarn install
yarn test
```

## pnpm
```sh
pnpm outdated
pnpm audit
pnpm up <pkg>@<version>
pnpm install
pnpm test
```

## pip
```sh
pip list --outdated --format=json
pip-audit                         # pip install pip-audit first
pip install -U <pkg>==<version>
pip freeze > requirements.txt     # regenerate pinned set (careful with extras)
pytest                            # gate
```

## poetry
```sh
poetry show --outdated
poetry add <pkg>@^<version>       # or: poetry update <pkg>
poetry lock --no-update           # regenerate lock without bumping others
poetry run pytest
```

## uv
```sh
uv pip list --outdated
uv lock --upgrade-package <pkg>
uv sync
uv run pytest
```

## cargo
```sh
cargo outdated                    # cargo install cargo-outdated
cargo audit                       # cargo install cargo-audit
cargo update -p <pkg> --precise <version>
cargo update                      # in-range updates
cargo test
cargo build --locked              # verify lockfile is honored
```

## go modules
```sh
go list -m -u all                 # show available upgrades
govulncheck ./...                 # vulnerabilities
go get <module>@<version>
go mod tidy                       # regenerate go.mod/go.sum
go test ./...
go build ./...
```

## bundler
```sh
bundle outdated
bundle audit                      # gem install bundler-audit; bundle audit check
bundle update <gem> --conservative
bundle install
bundle exec rspec
```

## composer
```sh
composer outdated
composer audit
composer require <vendor/pkg>:<constraint>
composer update <vendor/pkg> --with-dependencies
vendor/bin/phpunit
```

## maven / gradle
```sh
# maven
mvn versions:display-dependency-updates
mvn org.owasp:dependency-check-maven:check
mvn -DskipTests=false test

# gradle
./gradlew dependencyUpdates       # com.github.ben-manes.versions plugin
./gradlew test
```

## Notes
- Pin the package-manager version (e.g. `"packageManager"` field, `.tool-versions`,
  `corepack`) so lockfile regeneration does not churn unrelated entries.
- For Python, prefer poetry/uv lock semantics over `pip freeze` when a lockfile
  exists — freezing can drop extras and editable installs.
