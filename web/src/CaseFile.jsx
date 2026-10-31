import React, { useEffect, useState } from 'react'
import { api, inr, typo } from './api.js'
import { Gauge, WeeklyChart } from './charts.jsx'

export default function CaseFile({ id, onBack }) {
  const [d, setD] = useState(null)
  const [err, setErr] = useState(null)

  useEffect(() => {
    setD(null); setErr(null)
    if (id) api.caseFile(id).then(setD).catch((e) => setErr(e.message))
  }, [id])

  if (!id) return <div className="card pad"><p className="muted">Pick a case from the queue to open its file.</p><button className="btn" onClick={onBack}>Go to queue</button></div>
  if (err) return <div className="card pad"><p className="error">Could not load case: {err}</p></div>
  if (!d) return <div className="card pad"><p className="muted">Loading case…</p></div>

  const types = [...new Set(d.alerts.map((a) => a.typology))]
  const csv = () => {
    const head = 'typology,period_start,amount,detail\n'
    const body = d.alerts.map((a) => [a.typology, a.period_start, a.amount, `"${a.detail}"`].join(',')).join('\n')
    const url = URL.createObjectURL(new Blob([head + body], { type: 'text/csv' }))
    Object.assign(document.createElement('a'), { href: url, download: `${id}_evidence.csv` }).click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="stack">
      <button className="btn ghost" onClick={onBack}>← Back to queue</button>
      <div className="grid-case">
        <section className="card center">
          <Gauge value={d.score} />
          <h2 className="mono">{id}</h2>
          <p className="muted">{d.info.segment.replace('_', ' ').toLowerCase()} · declared income {inr(d.info.declared_monthly_income)} / month</p>
          <div className="chips">
            {types.map((t) => (
              <span key={t} className="chip" style={{ borderColor: typo(t).color, color: typo(t).color }}>{typo(t).label}</span>
            ))}
          </div>
          <button className="btn" onClick={csv}>Download evidence (CSV)</button>
        </section>

        <section className="card">
          <h3>Case summary <span className="tag">{d.summary_source === 'llm' ? 'AI-written from SQL evidence' : 'auto-generated'}</span></h3>
          <pre className="summary">{d.summary}</pre>
        </section>
      </div>

      <section className="card">
        <h3>Weekly money in vs out</h3>
        <p className="muted small">Non-cash transfers. Hover a bar for the exact amount.</p>
        <WeeklyChart data={d.weekly} />
      </section>

      <section className="card">
        <h3>Evidence <span className="count">{d.alerts.length}</span></h3>
        <ol className="timeline">
          {d.alerts.map((a, i) => (
            <li key={i}>
              <span className="tl-dot" style={{ background: typo(a.typology).color }} />
              <div>
                <div className="tl-top">
                  <b style={{ color: typo(a.typology).color }}>{typo(a.typology).label}</b>
                  <span className="muted small">{String(a.period_start).slice(0, 10)} · {inr(a.amount)}</span>
                </div>
                <div>{a.detail}</div>
              </div>
            </li>
          ))}
        </ol>
      </section>
    </div>
  )
}
