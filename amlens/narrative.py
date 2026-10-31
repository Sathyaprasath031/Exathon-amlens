"""Case-file narrative. Deterministic template by default.
If ANTHROPIC_API_KEY is set, an LLM may rewrite it, but it only ever sees the
evidence rows returned by SQL and is told to add nothing else."""
import json
import os

ACTIONS = {
    "STRUCTURING": "Review the cash deposit slips and branch CCTV; ask the customer for the source of cash.",
    "PASSTHROUGH": "Obtain the purpose of the inbound transfers and the relationship with the beneficiaries.",
    "FANIN_MULE": "Check whether the senders are victims of a scam; consider freezing outbound transfers.",
    "CIRCULAR": "Review all three linked accounts together; look for a common owner, device or address.",
    "INCOME_MISMATCH": "Refresh KYC: ask for updated income proof and the source of the extra funds.",
}


def build_template(account, alerts, score):
    seg, inc = account["segment"], float(account["declared_monthly_income"])
    lines = [f"Account {account['account_id']} ({seg.replace('_', ' ').title()}, declared monthly income "
             f"INR {inc:,.0f}) has a risk score of {score:.0f}/100."]
    for typ, grp in alerts.groupby("typology"):
        first, last = grp["period_start"].min(), grp["period_start"].max()
        lines.append(f"- {typ.replace('_', ' ').title()}: {len(grp)} alert(s) between {first} and {last}. "
                     f"Example: {grp.iloc[0]['detail']}.")
    lines.append("Suggested next steps:")
    for typ in alerts["typology"].unique():
        lines.append(f"- {ACTIONS[typ]}")
    lines.append("This is decision support. A human analyst must review the evidence before any report is filed.")
    return "\n".join(lines)


def build_narrative(account, alerts, score):
    text = build_template(account, alerts, score)
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return text, "template"
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        evidence = json.dumps({"account": account, "score": float(score),
                               "alerts": alerts.astype(str).to_dict("records")})
        msg = client.messages.create(
            model=os.getenv("AMLENS_LLM_MODEL", "claude-sonnet-4-6"), max_tokens=600,
            system=("You write short case summaries for a bank's AML analyst. Use ONLY the JSON evidence given. "
                    "Never invent facts, names or amounts. Mention each typology found, then list next steps. "
                    "End by stating that a human must review before any report is filed."),
            messages=[{"role": "user", "content": evidence}])
        return msg.content[0].text, "llm"
    except Exception as exc:  # fall back silently to the deterministic text
        return text + f"\n(LLM unavailable: {type(exc).__name__})", "template"
