const get = (url) =>
  fetch(url).then((r) => {
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`)
    return r.json()
  })

export const api = {
  summary: () => get('/api/summary'),
  queue: (min) => get(`/api/queue?min_score=${min}`),
  caseFile: (id) => get(`/api/case/${id}`),
  evaluation: () => get('/api/eval'),
  rules: () => get('/api/rules'),
}

export const inr = (n) =>
  'INR ' + new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(Number(n || 0))
export const num = (n) => new Intl.NumberFormat('en-IN').format(Number(n || 0))

export const TYPO = {
  STRUCTURING: { label: 'Structuring', color: '#d97706' },
  PASSTHROUGH: { label: 'Pass-through', color: '#0284c7' },
  FANIN_MULE: { label: 'Mule fan-in', color: '#7c3aed' },
  CIRCULAR: { label: 'Circular flow', color: '#db2777' },
  INCOME_MISMATCH: { label: 'Income mismatch', color: '#059669' },
}
export const typo = (t) => TYPO[t] || { label: t, color: '#94a3b8' }
