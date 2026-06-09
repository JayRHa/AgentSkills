# Worked Example: Rewriting a Weak Doc Section

This shows a real-world before/after for a single section, plus the reasoning. Use it as a model for the editing pass in the skill workflow (step 6).

---

## Source request

> "Document how users configure the database connection for the app."

Reader: a developer integrating the library. Intent: a specific task. Correct type: **how-to guide**.

---

## BEFORE (weak)

> ## Configuration
>
> In order to facilitate database connectivity, it is necessary for the configuration to be performed by the user. The application utilizes environment variables in order to determine how the connection should be established. Various settings can be configured, and it should be noted that the connection string is a critical component that must be provided. If the connection string is not provided, then errors will be encountered by the application during the initialization process. It is generally recommended that users simply set these variables prior to starting the application, as this is the easiest approach in most cases.

### What's wrong

- **Wrong altitude:** narrates *why* instead of giving steps for a task-oriented reader.
- **Passive voice everywhere:** "be performed by the user," "errors will be encountered," "can be configured."
- **Filler / weasel words:** *in order to, utilize, various, it should be noted, simply, generally, in most cases, easiest.*
- **No concrete example:** never names a variable or shows a value.
- **One dense paragraph:** no scannable structure, no expected output.
- **Vague:** "various settings" — which ones? "critical component" — say what it is.

Readability check (`scripts/readability.py`): high grade level, ~5 passive sentences, 8+ weasel words.

---

## AFTER (strong)

> ## How to configure the database connection
>
> > **Goal:** connect the app to your database using environment variables.
>
> ### Before you start
> - A reachable PostgreSQL database and its connection URL.
>
> ### Steps
>
> 1. **Set the connection string.** The app reads `DATABASE_URL`:
>    ```bash
>    export DATABASE_URL="postgres://user:pass@localhost:5432/myapp"
>    ```
>
> 2. **(Optional) Tune the pool.** Defaults work for most apps:
>    ```bash
>    export DB_POOL_SIZE=10        # max connections (default: 5)
>    export DB_TIMEOUT_MS=3000     # connect timeout (default: 5000)
>    ```
>
> 3. **Start the app.**
>    ```bash
>    ./app start
>    ```
>    On success you'll see:
>    ```
>    [info] connected to database myapp (pool=10)
>    ```
>
> ### Troubleshooting
>
> | Symptom | Cause | Fix |
> |---|---|---|
> | `error: DATABASE_URL is required` | Variable not set | Run the `export` in step 1 |
> | `error: connection refused` | DB not reachable | Check host/port and that the DB is running |

### Why it's better

- **Right type and altitude:** task title, goal statement, numbered steps.
- **Active voice + "you":** "Set the connection string," "you'll see."
- **Concrete:** names `DATABASE_URL`, shows real values, defaults, and expected output.
- **Scannable:** prerequisites, steps, troubleshooting table.
- **Honest specifics:** exact error strings and fixes instead of "errors will be encountered."

---

## The transformation in one line

From *"a paragraph explaining that configuration is necessary"* to *"a reader can copy three commands and be connected, and knows exactly what to do if it fails."*
