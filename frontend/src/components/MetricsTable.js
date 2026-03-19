export function renderMetricsTable(container, financials) {
  if (!financials) {
    container.innerHTML = `<div class="placeholder-state"><div class="icon">📊</div>재무 데이터 없음</div>`
    return
  }

  const rows = [
    { label: '매출', key: 'revenue', icon: '💰' },
    { label: '영업이익', key: 'operating_profit', icon: '📈' },
    { label: '성장률', key: 'growth_rate', icon: '🚀' },
    { label: '목표주가', key: 'target_price', icon: '🎯' },
  ]

  const tableRows = rows.map(({ label, key, icon }) => {
    const val = financials[key]
    return `
      <tr>
        <th>${icon} ${label}</th>
        <td class="${val ? 'value' : 'null'}">${val ?? '—'}</td>
      </tr>
    `
  }).join('')

  container.innerHTML = `
    <table class="fin-table">
      <tbody>${tableRows}</tbody>
    </table>
  `
}
