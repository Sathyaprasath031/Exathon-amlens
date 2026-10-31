import React, { useEffect, useMemo, useState } from 'react'
import { api, inr, num, typo } from './api.js'
import { Bar } from './charts.jsx'

const scoreClass = (s) => (s >= 70 ? 'hi' : s >= 40 ? 'mid' : 'lo')

export default function Overview({ summary, onOpen }) {
  const [min, setMin] = useState(40)
  const [rows, setRows] = useState([])
  const [filter, setFilter] = useState('')
  const [err, setErr] = useState(null)

  useEffect(() => {
    api.queue(min).then(setRows).catch((e) => setErr(e.message))
  }, [min])

  const shown = useMemo(
    () => rows.filter((r) => r.account_id.toLowerCase().includes(filter.toLowerCase())).slice(0, 150),
    [rows, filter],
  )
  const maxT = Math.max(...(summary?.typologies || []).map((t) => t.accounts), 1)

  return (
    <div className="stack">
      <div className="kpis">
        <Kpi label="Accounts scored" value={num(summary?.accounts)} />
        <Kpi label="Transactions analysed" value={num(summary?.txns)} />
        <Kpi label="Alerts raised" value={num(summary?.alerts)} />
        <Kpi label="Cases for review" value={num(summary?.flagged)} accent />
      </div>

      <div className="grid-2">
        <section className="card">
          <h3>Patterns found</h3>
          <p className="muted small">Accounts with at least one alert, by typology</p>
          {(summary?.typologies || []).map((t) => (
            <div className="trow" key={t.typology}>
              <span className="dot" style={{ background: typo(t.typology).color }} />
              <span className="tname">{typo(t.typology).label}</span>
              <Bar value={t.accounts / maxT} color={typo(t.typology).color} />
              <span className="tval">{num(t.accounts)}</span>
            </div>
          ))}
        </section>
        <section className="card">
          <h3>How to read this</h3>
          <ul className="how">
            <li><b>Score</b> combines every pattern found on an account (0 to 100). 40 and above goes to the queue.</li>
            <li><b>Click a case</b> to see the evidence, the weekly money flow and a plain-language summary.</li>
            <li><b>Thresholds</b> live in a database table, so a compliance officer can tune them.</li>
          </ul>
          <p className="notice">All data is synthetic. Decision support only: a person reviews every case.</p>
        </section>
      </div>

      <section className="card">
        <div className="queue-head">
          <h3>Case queue <span className="count">{num(rows.length)}</span></h3>
          <div className="controls">
            <input className="input" placeholder="Search account id" value={filter} onChange={(e) => setFilter(e.target.value)} />
            <label className="slider">
              Min score <b>{min}</b>
              <input type="range" min="0" max="100" step="5" value={min} onChange={(e) => setMin(+e.target.value)} />
            </label>
          </div>
        </div>
        {err && <p className="error">Could not load queue: {err}</p>}
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Score</th><th>Account</th><th>Segment</th><th>Declared income</th><th>Patterns</th><th>Amount involved</th><th>Active</th></tr>
            </thead>
            <tbody>
              {shown.map((r) => (
                <tr key={r.account_id} onClick={() => onOpen(r.account_id)}>
                  <td><span className={`pill ${scoreClass(r.risk_score)}`}>{Math.round(r.risk_score)}</span></td>
                  <td className="mono">{r.account_id}</td>
                  <td>{r.segment.replace('_', ' ').toLowerCase()}</td>
                  <td>{inr(r.declared_monthly_income)}</td>
                  <td>{r.n_typologies}</td>
                  <td>{inr(r.total_amount)}</td>
                  <td className="muted">{String(r.first_dt).slice(0, 10)} → {String(r.last_dt).slice(0, 10)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!shown.length && !err && <p className="muted pad">No cases at this score.</p>}
        </div>
      </section>
    </div>
  )
}

function Kpi({ label, value, accent }) {
  return (
    <div className={`kpi ${accent ? 'accent' : ''}`}>
      <div className="kpi-val">{value}</div>
      <div className="kpi-label">{label}</div>
    </div>
  )
}
