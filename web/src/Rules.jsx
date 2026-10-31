import React, { useEffect, useState } from 'react'
import { api } from './api.js'

export default function Rules() {
  const [d, setD] = useState(null)
  useEffect(() => { api.rules().then(setD).catch(() => setD({ config: [], weights: [], sql: '' })) }, [])
  if (!d) return <div className="card pad"><p className="muted">Loading rules…</p></div>
  return (
    <div className="stack">
      <div className="grid-2">
        <section className="card">
          <h3>Thresholds</h3>
          <p className="muted small">Rows in the <code>config</code> table. Change one with an SQL UPDATE and re-run the detectors.</p>
          <table className="static">
            <tbody>{d.config.map((c) => <tr key={c.param}><td className="mono">{c.param}</td><td>{c.val}</td></tr>)}</tbody>
          </table>
        </section>
        <section className="card">
          <h3>Pattern weights</h3>
          <table className="static">
            <tbody>{d.weights.map((w) => <tr key={w.typology}><td className="mono">{w.typology}</td><td>{w.weight}</td></tr>)}</tbody>
          </table>
          <p className="muted small">Score = sum of pattern scores (+10 per repeat, max 60 each), capped at 100.</p>
        </section>
      </div>
      <section className="card">
        <h3>Detector SQL (runs inside Exasol)</h3>
        <pre className="code">{d.sql}</pre>
      </section>
    </div>
  )
}
