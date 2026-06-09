# Worked Example: Messy Input → Inclusive JD

## Raw input from hiring manager
> Need a backend rockstar ninja. Must have CS degree + 10 years experience. Expert in
> Python, Go, Rust, Kubernetes, Postgres, Kafka, Terraform, AWS, gRPC. Young energetic
> self-starter who can work in our fast-paced family. We work hard play hard. Aggressive
> go-getter. Reports to eng lead. Payments team. Remote-ish. They'll work on backend stuff.

## Problems detected (and by `jd_lint.py`)
- `bias`: "rockstar", "ninja", "young energetic", "aggressive".
- `inflation`: "10 years", CS degree required, 9 named technologies as must-have.
- `jargon`: "fast-paced", "work hard play hard", "we are a family".
- Vague responsibilities ("backend stuff"); no outcomes, comp, or EEO.

## Finished job description

# Senior Backend Engineer, Payments (Senior / IC4)

## About the role
Payments is the backbone of our business — every transaction our customers make flows
through the services this team owns. We're hiring a Senior Backend Engineer to make
payments faster, more reliable, and easier to extend as we expand into new markets.

## About the team
The Payments team (6 engineers) owns the services that authorize, route, and settle
payments. You'll report to the Payments Engineering Lead and work closely with Product,
Finance, and Security.

## What you'll do
- Own the reliability of the core payments service, driving down latency and error rates.
- Design and ship new payment-method integrations end-to-end, from API to settlement.
- Lead architectural decisions for the team and mentor mid-level engineers.
- Partner with Security and Finance to keep transactions correct, auditable, and compliant.
- Improve our observability so on-call is calm and incidents are rare and short.

## What success looks like
- **By 90 days:** You've shipped a meaningful improvement to the payments pipeline and are on-call confidently.
- **By 1 year:** You've led at least one major integration and measurably improved a reliability metric.

## What you'll bring (must-have)
- Demonstrated experience building and operating reliable backend services in production.
- Strong skills in a systems-oriented language (e.g., Go, Rust, or Python) — we don't require all three.
- Experience with relational databases (e.g., Postgres) and designing for data correctness.
- A track record of owning projects end-to-end and mentoring others.

## Nice to have
- Experience with Kubernetes, Kafka, gRPC, or Terraform, or similar tools.
- Background in payments, fintech, or another high-correctness domain.

## Compensation & benefits
- **Salary range:** $150,000–$190,000 / year + equity + annual bonus.
- **Benefits:** Full health/dental/vision, 25 days PTO, $2,000 learning budget, 16 weeks parental leave, remote work stipend.

## Logistics
- **Location / work model:** Remote within the US (UTC-5 to UTC-8 overlap required).
- **Employment type:** Full-time.
- **Visa sponsorship:** Available.
- **Hiring process:** Recruiter screen → technical conversation → system design + collaboration → team meet. ~3 weeks.

## How to apply
Apply with your resume and a short note on a backend system you're proud of. If you're
excited about this role but don't meet every requirement, we still encourage you to apply.

## Equal opportunity
We are an equal-opportunity employer committed to an inclusive workplace and do not
discriminate on the basis of any protected characteristic. We provide reasonable
accommodations throughout the hiring process — let us know what you need.

---

### Before / after lines
| Before | After |
|---|---|
| "backend rockstar ninja" | "Senior Backend Engineer" |
| "CS degree + 10 years" | "Demonstrated experience building and operating reliable backend services" |
| "Expert in [9 technologies]" | 3 core must-haves + the rest moved to nice-to-have ("or similar") |
| "young energetic" / "aggressive go-getter" | removed; replaced with concrete outcomes |
| "They'll work on backend stuff" | 5 outcome-based responsibility bullets |
| (no comp, no EEO) | salary range + benefits + EEO statement |
