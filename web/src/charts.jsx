import React from 'react'
import { inr } from './api.js'

export function Gauge({ value }) {
  const r = 52, c = 2 * Math.PI * r
  const v = Math.max(0, Math.min(100, value))
  const color = v >= 70 ? '#e11d48' : v >= 40 ? '#d97706' : '#059669'
  return (
    <svg viewBox="0 0 140 140" className="gauge" role="img" aria-label={`Risk score ${v}`}>
      <circle cx="70" cy="70" r={r} fill="none" stroke="rgba(15,23,42,.08)" strokeWidth="12" />
      <circle cx="70" cy="70" r={r} fill="none" stroke={color} strokeWidth="12" strokeLinecap="round"
        strokeDasharray={`${(v / 100) * c} ${c}`} transform="rotate(-90 70 70)"
        style={{ filter: `drop-shadow(0 2px 6px ${color}55)` }} />
      <text x="70" y="72" textAnchor="middle" className="gauge-num">{Math.round(v)}</text>
      <text x="70" y="94" textAnchor="middle" className="gauge-sub">of 100</text>
    </svg>
  )
}

export function WeeklyChart({ data }) {
  if (!data.length) return <p className="muted">No non-cash flows for this account.</p>
  const W = 680, H = 230, pl = 54, pb = 28, pt = 12
  const max = Math.max(...data.flatMap((d) => [d.cr_nc, d.dr_nc]), 1)
  const bw = (W - pl - 8) / data.length
  const y = (v) => pt + (H - pt - pb) * (1 - v / max)
  const fmt = (v) => (v >= 1e5 ? `${(v / 1e5).toFixed(1)}L` : `${Math.round(v / 1e3)}k`)
  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} className="chart">
        {[0, 0.5, 1].map((t) => (
          <g key={t}>
            <line x1={pl} x2={W - 8} y1={y(max * t)} y2={y(max * t)} stroke="rgba(15,23,42,.08)" />
            <text x={pl - 8} y={y(max * t) + 4} textAnchor="end" className="tick">{fmt(max * t)}</text>
          </g>
        ))}
        {data.map((d, i) => {
          const x = pl + i * bw
          const w = Math.max(3, bw * 0.34)
          return (
            <g key={d.wk_start}>
              <rect x={x + bw * 0.12} y={y(d.cr_nc)} width={w} height={H - pb - y(d.cr_nc)} rx="2" fill="url(#gin)">
                <title>{`${d.wk_start}  in: ${inr(d.cr_nc)}`}</title>
              </rect>
              <rect x={x + bw * 0.12 + w + 1} y={y(d.dr_nc)} width={w} height={H - pb - y(d.dr_nc)} rx="2" fill="url(#gout)">
                <title>{`${d.wk_start}  out: ${inr(d.dr_nc)}`}</title>
              </rect>
              {i % 3 === 0 && (
                <text x={x + bw / 2} y={H - 8} textAnchor="middle" className="tick">{d.wk_start.slice(5)}</text>
              )}
            </g>
          )
        })}
        <defs>
          <linearGradient id="gin" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#14b8a6" /><stop offset="1" stopColor="#0d9488" />
          </linearGradient>
          <linearGradient id="gout" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#6366f1" /><stop offset="1" stopColor="#4338ca" />
          </linearGradient>
        </defs>
      </svg>
      <div className="legend"><span><i style={{ background: '#0d9488' }} />Money in</span><span><i style={{ background: '#4f46e5' }} />Money out</span></div>
    </div>
  )
}

export function Bar({ value, color = 'var(--accent)' }) {
  return (
    <div className="bar"><div style={{ width: `${Math.max(0, Math.min(1, value)) * 100}%`, background: color }} /></div>
  )
}
