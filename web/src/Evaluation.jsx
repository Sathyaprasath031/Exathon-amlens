import React, { useEffect, useState } from 'react'
import { api, num, typo } from './api.js'
import { Bar } from './charts.jsx'

export default function Evaluation() {
  const [d, setD] = useState(null)
  const [err, setErr] = useState(null)
  useEffect(() => { api.evaluation().then(setD).catch((e) => setErr(e.message)) }, [])
  if (err) return <div className="card pad"><p className="error">{err}</p></div>
  if (!d) return <div className="card pad"><p className="muted">Computing in Exasol…</p></div>

  return (
    <div className="stack">
      <div className="notice big">
        Measured against the <b>{num(d.planted)}</b> suspicious accounts our own generator planted. This shows the
        pipeline works end to end. It is <b>not</b> a claim about accuracy on real bank data.
      </div>
      <div className="grid-2">
        {d.methods.map((m, i) => (
          <section className={`card ${i === 0 ? 'glow' : ''}`} key={m.method}>
            <h3>{m.method}</h3>
            <div className="big-stat">{num(m.flagged)}<span> accounts flagged</span></div>
            <div className="metric"><span>Precision</span><Bar value={m.precision} color={i === 0 ? '#0d9488' : '#94a3b8'} /><b>{(m.precision * 100).toFixed(1)}%</b></div>
            <div className="metric"><span>Recall</span><Bar value={m.recall} color={i === 0 ? '#4f46e5' : '#94a3b8'} /><b>{(m.recall * 100).toFixed(1)}%</b></div>
            <p className="muted small">{num(m.true_pos)} correct · {num(m.false_alarms)} false alarms</p>
          </section>
        ))}
      </div>
      <section className="card">
        <h3>By pattern</h3>
        <div className="table-wrap">
          <table className="static">
            <thead><tr><th>Pattern</th><th>Planted</th><th>Found by its detector</th><th>Flagged by score</th><th>Found by baseline rule</th></tr></thead>
            <tbody>
              {d.typologies.map((t) => (
                <tr key={t.typology}>
                  <td><span className="dot" style={{ background: typo(t.typology).color }} /> {typo(t.typology).label}</td>
                  <td>{num(t.n_planted)}</td><td>{num(t.caught_by_own_detector)}</td>
                  <td>{num(t.flagged_by_score)}</td><td>{num(t.flagged_by_baseline)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
