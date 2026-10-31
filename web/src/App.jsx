import React, { useEffect, useState } from 'react'
import { api } from './api.js'
import Overview from './Overview.jsx'
import CaseFile from './CaseFile.jsx'
import Evaluation from './Evaluation.jsx'
import Rules from './Rules.jsx'

const TABS = [['overview', 'Overview'], ['case', 'Case file'], ['eval', 'Does it work?'], ['rules', 'Rules & SQL']]

export default function App() {
  const [tab, setTab] = useState('overview')
  const [caseId, setCaseId] = useState(null)
  const [summary, setSummary] = useState(null)
  const [err, setErr] = useState(null)

  useEffect(() => { api.summary().then(setSummary).catch((e) => setErr(e.message)) }, [])
  const open = (id) => { setCaseId(id); setTab('case') }

  return (
    <div className="app">
      <header className="top">
        <div className="brand">
          <svg viewBox="0 0 32 32" width="34" height="34" aria-hidden="true">
            <defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#0d9488" /><stop offset="1" stopColor="#4f46e5" /></linearGradient></defs>
            <circle cx="14" cy="14" r="9" fill="none" stroke="url(#lg)" strokeWidth="3" />
            <line x1="21" y1="21" x2="28" y2="28" stroke="url(#lg)" strokeWidth="3.5" strokeLinecap="round" />
            <circle cx="14" cy="14" r="3" fill="url(#lg)" />
          </svg>
          <div><div className="brand-name">AMLens</div><div className="brand-sub">AML case triage · powered by Exasol Personal</div></div>
        </div>
        <nav className="tabs">
          {TABS.map(([k, label]) => (
            <button key={k} className={tab === k ? 'on' : ''} onClick={() => setTab(k)}>{label}</button>
          ))}
        </nav>
      </header>
      <main>
        {err && (
          <div className="card pad">
            <p className="error">Cannot reach the API ({err}). Start it with <code>uvicorn api:app --port 8000</code> and make sure the pipeline has been run.</p>
          </div>
        )}
        {!err && tab === 'overview' && <Overview summary={summary} onOpen={open} />}
        {!err && tab === 'case' && <CaseFile id={caseId} onBack={() => setTab('overview')} />}
        {!err && tab === 'eval' && <Evaluation />}
        {!err && tab === 'rules' && <Rules />}
      </main>
      <footer>Synthetic data only · MIT licence · ExaThon India 2026 · Track: Money, Risk &amp; Regulation</footer>
    </div>
  )
}
