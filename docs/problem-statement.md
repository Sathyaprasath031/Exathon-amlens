# Problem statement

**Track:** Money, Risk & Regulation

> A compliance analyst at a mid-size Indian bank or cooperative bank can't tell which of today's
> thousands of alerts deserve an investigation, because single-transaction threshold rules flag
> big but innocent business deposits and miss patterns that only show up across many transactions
> and many accounts. If this worked, she would open a short, ranked queue where every case already
> shows the pattern, the amounts, the dates and a suggested next step.

## Who has the problem and why it matters

Banks must monitor accounts for money laundering and report suspicious activity to FIU-IND.
The common first line of defence is a static rule such as "alert on any cash transaction of
INR 10 lakh or more". Two things go wrong:

1. **False alarms drown the team.** Legitimate businesses make large deposits every day. Each alert needs
   a human to open it, so real cases wait in the queue.
2. **Layered behaviour slips through.** Launderers avoid single big transactions. They split deposits just under
   a limit (structuring), park money for a day and send it on (pass-through), collect many small payments
   into one account (mule fan-in), move money in a circle between linked accounts, or push far more
   money through an account than its declared income supports.

Each of these patterns needs weeks of history across millions of rows and a view of the money-flow graph.
That is a database problem, not a rules-engine problem.

## What AMLens does

It loads transactions into Exasol Personal and, entirely in SQL:

- builds weekly and monthly account features and a directed money-flow graph;
- runs five typology detectors (structuring, pass-through, fan-in mule, circular flow, income mismatch);
- uses **segment-aware thresholds** (a business account is judged against business behaviour);
- rolls alerts into one explainable 0-100 score per account;
- serves a ranked case queue and a case file (evidence, weekly flow chart, plain-language summary,
  suggested next steps) to the analyst.

Thresholds are rows in a `config` table. A compliance officer can tune a rule with one `UPDATE`.

## What changes for the analyst

| Today | With AMLens |
|---|---|
| One alert per big transaction | One case per account, ranked by score |
| "Why was this flagged?" needs manual digging | Each alert carries its own evidence sentence |
| Patterns across accounts are invisible | Circular flows and mule collectors are found in the graph |
| Rule changes need a code release | Rule change is one SQL `UPDATE` |

## Honest limits

- The data is synthetic and the patterns were planted by us. Results show that the pipeline and SQL logic work,
  not what accuracy a real bank would see.
- AMLens is decision support. It does not file reports and it does not decide who is guilty.
- Business accounts get relaxed thresholds, so a launderer hiding inside a business account is harder to catch.
