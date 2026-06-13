# Worked example: React 17 -> 18 major upgrade (npm)

A concrete run of the workflow for a single high-risk major bump.

## 1. Baseline
```sh
$ git status
nothing to commit, working tree clean
$ git rev-parse HEAD
9f3c1a2   # <-- BASELINE / rollback anchor
$ npm test
Test Suites: 42 passed, 42 total   # green before we start
```

## 2. Inventory
```sh
$ python3 scripts/check_outdated.py --dir .
Ecosystem detected: npm
6 outdated package(s):

PACKAGE        CURRENT  LATEST   TIER
-------------------------------------------
react          17.0.2   18.3.1   major  <-- isolate
react-dom      17.0.2   18.3.1   major  <-- isolate
@types/react   17.0.83  18.3.12  major  <-- isolate
lodash         4.17.20  4.17.21  patch
axios          1.6.2    1.7.7    minor
jest           29.7.0   29.7.0   none

Summary: 3 major (isolate, one commit each), 1 minor, 1 patch.
```

## 3. Plan
- Front of queue: nothing has a CVE here.
- Batch safe: `lodash` (patch) + `axios` (minor) -> one commit.
- Isolated group: `react` + `react-dom` + `@types/react` must move **together**
  (peer deps + matching types). React's major guide is required reading.

## 4. Safe batch
```sh
$ npm install lodash@4.17.21 axios@1.7.7
$ npm test            # green
$ git add package.json package-lock.json
$ git commit -m "chore(deps): upgrade lodash and axios (patch/minor)"
```

## 5. React major (read changelog FIRST)
From the React 18 upgrade guide, breaking items that touch this codebase:
- `ReactDOM.render` is deprecated -> use `createRoot`.
- Stricter `StrictMode` double-invokes effects in dev.
- `@types/react` 18 tightens children typing (no implicit `children`).

```sh
$ npm install react@18.3.1 react-dom@18.3.1 @types/react@18.3.12
```
Apply the code change the guide demands:
```diff
- import ReactDOM from 'react-dom';
- ReactDOM.render(<App />, document.getElementById('root'));
+ import { createRoot } from 'react-dom/client';
+ createRoot(document.getElementById('root')!).render(<App />);
```
Fix the type errors surfaced by `@types/react` 18 (add explicit
`children: React.ReactNode` to components that need it).

```sh
$ npm test
FAIL  src/Modal.test.tsx  (effect ran twice under StrictMode)
```
The failure is clear and small (a test asserting single effect invocation).
Fix forward: make the effect idempotent and update the assertion. Re-run:
```sh
$ npm test            # 42 passed
$ npm run build       # framework upgrade: build + smoke matter
$ git add package.json package-lock.json src/index.tsx src/Modal.tsx src/Modal.test.tsx
$ git commit -m "chore(deps): upgrade react/react-dom 17.0.2 -> 18.3.1

- Migrate ReactDOM.render -> createRoot (React 18 root API)
- Add explicit children typing for @types/react 18
- Make Modal effect idempotent (StrictMode double-invoke)
- Changelog: https://react.dev/blog/2022/03/29/react-v18"
```

## If it had gone sideways
Suppose the build broke in a way that needed a large refactor of a routing
library that wasn't React-18 ready. Don't leave it red — roll back just this
upgrade:
```sh
$ git restore --source=HEAD --staged --worktree package.json package-lock.json
$ npm ci
$ npm test            # green again, back at the safe-batch commit
```
Then report: "React 18 blocked by react-router@5 (needs v6, separate
migration). Deferred; tracking in issue #123."

## 6. Report
Fill `templates/upgrade-report.md`: 3 upgraded (react/react-dom/@types/react as
one logical major + lodash/axios batch), 0 deferred, rollback anchor `9f3c1a2`.
