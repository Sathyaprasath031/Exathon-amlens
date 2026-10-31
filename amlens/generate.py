"""Synthetic bank data with planted money-laundering typologies.

Everything here is invented. No real customer, bank or employer data is used.
Amounts are in INR. The 4-month period is 2026-01-01 .. 2026-04-30.
"""
import numpy as np
import pandas as pd
from datetime import date

START = date(2026, 1, 1)
NDAYS = 120
MONTH_OFF = np.array([0, 31, 59, 90])
MONTH_LEN = np.array([31, 28, 31, 30])
WEEK_BASE = 4 + 7 * np.arange(16)          # Monday-aligned week starts (offsets)
SCALES = {"tiny": 2_000, "small": 10_000, "medium": 50_000, "large": 250_000}
SEGMENTS = ["SALARIED", "SELF_EMPLOYED", "STUDENT", "BUSINESS"]


class _Events:
    def __init__(self):
        self.parts = []

    def add(self, acc, day, amt, direction, channel, cp):
        acc = np.asarray(acc)
        if acc.size == 0:
            return
        self.parts.append(pd.DataFrame({
            "acc": acc, "day": np.asarray(day), "amt": np.round(np.asarray(amt, dtype=float), 2),
            "direction": direction, "channel": channel, "cp": cp}))

    def transfer(self, ids, src, dst, day, amt, channel):
        """Move money between two accounts of this bank: debit leg + credit leg."""
        src, dst = np.asarray(src), np.asarray(dst)
        self.add(src, day, amt, "DEBIT", channel, ids[dst])
        self.add(dst, day, amt, "CREDIT", channel, ids[src])


def _ext(prefix, n, hi, rng):
    return np.char.add(prefix, rng.integers(0, hi, n).astype(str))


def generate(scale="small", seed=42):
    rng = np.random.default_rng(seed)
    n = SCALES[scale] if scale in SCALES else int(scale)
    ids = np.array([f"A{i:07d}" for i in range(n)])

    seg = rng.choice(SEGMENTS, size=n, p=[.55, .20, .10, .15])
    med = {"SALARIED": (45_000, .45), "SELF_EMPLOYED": (55_000, .6),
           "STUDENT": (8_000, .4), "BUSINESS": (1_500_000, .6)}
    income = np.array([med[s][0] * np.exp(rng.normal(0, med[s][1])) for s in seg])
    income = np.round(income, -2)
    landlord = (np.isin(seg, ["SALARIED", "SELF_EMPLOYED"])) & (rng.random(n) < .03)

    # ---- choose accounts for planted typologies (never landlords / businesses)
    pool = np.where(np.isin(seg, ["SALARIED", "SELF_EMPLOYED", "STUDENT"]) & ~landlord)[0]
    rng.shuffle(pool)
    k = lambda f, lo: max(lo, int(f * n))
    n_s, n_p, n_f, n_i, n_r = k(.004, 6), k(.003, 5), k(.004, 6), k(.004, 6), k(.0025, 4)
    cur = 0

    def grab(m):
        nonlocal cur
        out = pool[cur:cur + m]
        cur += m
        return out

    a_struct, a_pt, a_fan, a_inc = grab(n_s), grab(n_p), grab(n_f), grab(n_i)
    rings = grab(3 * n_r).reshape(n_r, 3)

    # income-mismatch accounts declare a low income
    income[a_inc] = np.round(rng.uniform(10_000, 30_000, len(a_inc)), -2)
    seg[a_inc] = np.where(rng.random(len(a_inc)) < .5, "SALARIED", "STUDENT")

    ev = _Events()
    seg_k = {"SALARIED": 1, "SELF_EMPLOYED": 3, "STUDENT": 1, "BUSINESS": 30}
    spend_k = {"SALARIED": 22, "SELF_EMPLOYED": 22, "STUDENT": 15, "BUSINESS": 25}
    spend_f = {"SALARIED": .70, "SELF_EMPLOYED": .75, "STUDENT": .90, "BUSINESS": .85}

    for m in range(4):
        off, ln = MONTH_OFF[m], MONTH_LEN[m]
        for s in SEGMENTS:
            idx = np.where(seg == s)[0]
            # income credits
            kk = seg_k[s]
            a = np.repeat(idx, kk)
            day = off + (rng.integers(0, 5, a.size) if s in ("SALARIED", "STUDENT") else rng.integers(0, ln, a.size))
            amt = income[a] / kk * np.exp(rng.normal(0, .15, a.size))
            ch = "NEFT" if s in ("SALARIED", "STUDENT") else rng.choice(["UPI", "NEFT", "IMPS"], a.size)
            cp = _ext("EXT_ER", a.size, 3000, rng) if s == "SALARIED" else _ext("EXT_C", a.size, 8000, rng)
            ev.add(a, day, amt, "CREDIT", ch, cp)
            # spending
            kk = spend_k[s]
            a = np.repeat(idx, kk)
            amt = income[a] * spend_f[s] / kk * np.exp(rng.normal(0, .6, a.size) - .18)
            ch = rng.choice(["UPI", "NEFT"], a.size) if s == "BUSINESS" else "UPI"
            ev.add(a, off + rng.integers(0, ln, a.size), amt, "DEBIT", ch, _ext("EXT_M", a.size, 5000, rng))

        # small peer-to-peer transfers between customers (non-business)
        nb = np.where(seg != "BUSINESS")[0]
        cnt = rng.poisson(3, nb.size)
        src = np.repeat(nb, cnt)
        dst = (src + rng.integers(1, n, src.size)) % n
        ev.transfer(ids, src, dst, off + rng.integers(0, ln, src.size),
                    np.exp(rng.normal(7.3, .8, src.size)), "UPI")
        # small cash deposits (non-business) and large business cash deposits
        cnt = rng.poisson(.6, nb.size)
        a = np.repeat(nb, cnt)
        ev.add(a, off + rng.integers(0, ln, a.size), rng.uniform(2_000, 30_000, a.size), "CREDIT", "CASH", "CASH")
        bz = np.where(seg == "BUSINESS")[0]
        a = np.repeat(bz, 8)
        ev.add(a, off + rng.integers(0, ln, a.size), income[a] * .1 * np.exp(rng.normal(0, .8, a.size)),
               "CREDIT", "CASH", "CASH")

    # landlords: rent from many tenants, spent normally (benign fan-in look-alike)
    for m in range(4):
        ll = np.repeat(np.where(landlord)[0], 8)
        ev.add(ll, MONTH_OFF[m] + rng.integers(0, 5, ll.size), rng.uniform(8_000, 25_000, ll.size),
               "CREDIT", "UPI", _ext("EXT_T", ll.size, 4000, rng))
    # a few students receive a one-off lump sum from parents (benign income outlier)
    st = np.where((seg == "STUDENT") & (rng.random(n) < .03))[0]
    ev.add(st, rng.integers(0, NDAYS, st.size), rng.uniform(150_000, 300_000, st.size), "CREDIT", "NEFT",
           _ext("EXT_PAR", st.size, 3000, rng))

    gt = []
    # ---- STRUCTURING: repeated cash deposits just under the 50,000 PAN limit
    for a in a_struct:
        gt.append((ids[a], "STRUCTURING"))
        for w in rng.choice(16, rng.integers(3, 6), replace=False):
            nd = rng.integers(5, 9)
            amts = np.round(rng.uniform(45_000, 49_900, nd), -2)
            ev.add([a] * nd, WEEK_BASE[w] + rng.integers(0, 5, nd), amts, "CREDIT", "CASH", "CASH")
            ev.add([a], [WEEK_BASE[w] + 6], [amts.sum() * .9], "DEBIT", "NEFT", f"EXT_B{rng.integers(0, 999)}")
    # ---- PASSTHROUGH: large credit leaves within days
    for a in a_pt:
        gt.append((ids[a], "PASSTHROUGH"))
        for w in rng.choice(16, rng.integers(3, 6), replace=False):
            tot = rng.uniform(600_000, 1_500_000)
            ki, ko = rng.integers(1, 4), rng.integers(1, 4)
            ev.add([a] * ki, WEEK_BASE[w] + rng.integers(0, 3, ki), [tot / ki] * ki, "CREDIT", "NEFT",
                   _ext("EXT_X", ki, 9000, rng))
            out = tot * rng.uniform(.93, .98)
            ev.add([a] * ko, WEEK_BASE[w] + rng.integers(3, 6, ko), [out / ko] * ko, "DEBIT", "IMPS",
                   _ext("EXT_P", ko, 9000, rng))
    # ---- FANIN_MULE: many small payments from different people, then one big transfer out
    for a in a_fan:
        gt.append((ids[a], "FANIN_MULE"))
        benef = f"EXT_MULE{rng.integers(0, 99999)}"
        for w in rng.choice(16, rng.integers(3, 6), replace=False):
            ni = rng.integers(10, 26)
            victims = (a + rng.integers(1, n, ni)) % n
            amts = rng.uniform(8_000, 15_000, ni)
            ev.transfer(ids, victims, [a] * ni, WEEK_BASE[w] + rng.integers(0, 5, ni), amts, "UPI")
            ev.add([a, a], [WEEK_BASE[w] + 5, WEEK_BASE[w] + 6], [amts.sum() * .45 * rng.uniform(.9, 1.05)] * 2,
                   "DEBIT", "IMPS", benef)
    # ---- CIRCULAR: A -> B -> C -> A with near-identical amounts
    for r in rings:
        for a in r:
            gt.append((ids[a], "CIRCULAR"))
        for w in rng.choice(16, rng.integers(3, 6), replace=False):
            x = rng.uniform(150_000, 400_000)
            d = WEEK_BASE[w] + rng.integers(0, 3)
            ev.transfer(ids, [r[0]], [r[1]], [d], [x], "NEFT")
            ev.transfer(ids, [r[1]], [r[2]], [d + 1], [x * rng.uniform(.97, .99)], "NEFT")
            ev.transfer(ids, [r[2]], [r[0]], [d + 2], [x * rng.uniform(.94, .98)], "NEFT")
    # ---- INCOME_MISMATCH: credits far above declared income, month after month
    for a in a_inc:
        gt.append((ids[a], "INCOME_MISMATCH"))
        for m in range(4):
            nc = rng.integers(5, 9)
            tot = rng.uniform(400_000, 900_000)
            ev.add([a] * nc, MONTH_OFF[m] + rng.integers(0, MONTH_LEN[m], nc), [tot / nc] * nc, "CREDIT",
                   rng.choice(["UPI", "NEFT"], nc), _ext("EXT_C", nc, 8000, rng))
            ev.add([a] * 2, MONTH_OFF[m] + rng.integers(0, MONTH_LEN[m], 2), [tot * .1] * 2, "DEBIT", "UPI",
                   _ext("EXT_M", 2, 5000, rng))

    t = pd.concat(ev.parts, ignore_index=True)
    t = t[(t.day >= 0) & (t.day < NDAYS)].sort_values("day", kind="stable").reset_index(drop=True)
    dts = pd.to_datetime(START) + pd.to_timedelta(t["day"].to_numpy(), unit="D")
    wk = dts - pd.to_timedelta(dts.day_of_week, unit="D")
    mth = dts.to_period("M").to_timestamp()
    fmt = lambda x: pd.Series(x).dt.strftime("%Y-%m-%d").to_numpy()
    txns = pd.DataFrame({
        "txn_id": np.arange(1, len(t) + 1, dtype="int64"),
        "account_id": ids[t["acc"].to_numpy()],
        "counterparty_id": t["cp"].to_numpy(),
        "direction": t["direction"].to_numpy(),
        "channel": t["channel"].to_numpy(),
        "amount": t["amt"].to_numpy(),
        "txn_dt": fmt(dts), "txn_hour": rng.integers(8, 21, len(t)).astype("int16"),
        "wk_start": fmt(wk), "mth_start": fmt(mth)})
    accounts = pd.DataFrame({
        "account_id": ids, "segment": seg, "declared_monthly_income": income,
        "opened_dt": fmt(pd.to_datetime(START) - pd.to_timedelta(rng.integers(30, 3650, n), unit="D")),
        "branch": [f"BR{b:02d}" for b in rng.integers(1, 41, n)]})
    gt_df = pd.DataFrame(gt, columns=["account_id", "typology"])
    return accounts, txns, gt_df


if __name__ == "__main__":
    a, t, g = generate("tiny")
    print(len(a), "accounts,", len(t), "transactions")
    print(g.typology.value_counts())
