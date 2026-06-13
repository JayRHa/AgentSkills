---
name: personal-budget-planner
description: Builds a realistic personal or household budget from income and expenses — choosing a budgeting method (50/30/20, zero-based, envelopes), categorizing spending, setting savings and debt-payoff targets, and producing a monthly plan with an emergency-fund and debt strategy. Use this skill when a user asks to "make me a budget", "help me manage my money", "where is my money going", "save more / pay off debt", "monthly budget", or wants a household spending plan.
license: MIT
---

# Personal Budget Planner

## Overview
This skill turns income and spending into a clear monthly budget that funds essentials, savings goals, and debt payoff. It picks an appropriate budgeting method, categorizes expenses, finds room to redirect, and lays out an emergency-fund and debt strategy — in plain language, with the math shown.

**Keywords**: budget, personal finance, household budget, saving, spending plan, 50/30/20, zero-based budget, envelope method, emergency fund, debt payoff, snowball, avalanche, cash flow.

## When to use vs. not
Use this for everyday budgeting, saving, and consumer-debt payoff planning. This is **financial education, not licensed financial/tax/investment advice**. For investing specifics, taxes, bankruptcy, or complex debt, recommend a qualified professional (CFP, accountant, nonprofit credit counselor). Don't recommend specific securities or guarantee returns.

## Inputs to gather first
1. **Net (take-home) income** and frequency; note any variable/irregular income.
2. **Fixed expenses** (rent/mortgage, utilities, insurance, subscriptions, loan minimums).
3. **Variable expenses** (groceries, transport, eating out, fun).
4. **Debts**: balances, interest rates, minimums.
5. **Goals**: emergency fund, a purchase, debt-free date, savings rate.
6. **Currency/region** and household size.

## Workflow
1. **Total the income.** Use *net* income. For variable income, budget on a conservative average or last few months' low. 
2. **List and categorize expenses** into Needs, Wants, and Savings/Debt. Pull from statements if available; estimate honestly otherwise. Flag subscriptions and "leaks."
3. **Pick a method** that fits the user. 50/30/20 for simplicity, zero-based for control, envelopes for overspenders. See `references/methods.md`.
4. **Compare to a benchmark.** Map current spending onto the chosen method and show the gaps (e.g., "Needs are 68% of income vs. a 50% target"). This reveals where the pressure is.
5. **Build the emergency fund first.** A starter $1,000-equivalent, then 3–6 months of essential expenses, held in an accessible account. This is the foundation before aggressive investing.
6. **Choose a debt strategy.** Avalanche (highest interest first — least cost) or snowball (smallest balance first — most motivation). Show both and let the user pick. See `references/debt-payoff.md`.
7. **Assign every category a number** and reconcile so income − expenses − savings − debt = 0 (zero-based) or fits the method's ratios. Cut Wants first when over.
8. **Make it sustainable + trackable.** Automate savings/debt transfers on payday ("pay yourself first"), set a weekly money check-in, and give a simple tracking format. Schedule a monthly review to adjust.

## Decision framework
| Situation | Recommend |
| --- | --- |
| Wants a simple start | 50/30/20 |
| Overspends, needs control | Zero-based or envelope/cash |
| Variable income | Budget on a low-average month; buffer category |
| High-interest debt | Avalanche; pause non-essential extras until cleared |
| Needs motivation to stick | Snowball; celebrate each cleared debt |
| No savings buffer | Emergency fund before extra debt payoff beyond minimums |

## Worked example
See `examples/monthly-budget.md` for a full 50/30/20 build with a debt-payoff plan.

## Best Practices
- **Use net income**, not gross.
- **Pay yourself first** — automate savings on payday before spending.
- **Build an emergency fund** before investing or aggressive extra payoff.
- **Track for a month** to see real numbers; estimates always understate the small stuff.
- **Cut Wants, protect Needs.** Find leaks in subscriptions and eating out.
- **Review monthly** — a budget is a living plan, not a one-time spreadsheet.

## Common Pitfalls
- **Budgeting gross income** you never actually receive.
- **Forgetting irregular expenses** (annual insurance, gifts, car repairs) — use sinking funds.
- **Unrealistic cuts** that collapse in week two.
- **No emergency fund** → any surprise becomes new debt.
- **Ignoring interest rates** when ordering debt payoff.
- **Set-and-forget** — life changes; the budget must too.
- **Treating this as licensed advice** — flag the limits and refer out for investing/tax/legal.
