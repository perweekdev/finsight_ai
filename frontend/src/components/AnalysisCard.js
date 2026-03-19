export function renderAnalysisCard(container, analysis) {
  if (!analysis || Object.keys(analysis).length === 0) {
    container.innerHTML = `<div class="placeholder-state"><div class="icon">🔍</div>분석 데이터 없음</div>`
    return
  }

  const { company_name, overview, bull_case = [], bear_case = [], key_issues = [] } = analysis

  const bullItems = bull_case.map(item => `<li>${item}</li>`).join('') || '<li style="color:var(--text3)">데이터 없음</li>'
  const bearItems = bear_case.map(item => `<li>${item}</li>`).join('') || '<li style="color:var(--text3)">데이터 없음</li>'
  const issueTags = key_issues.length
    ? key_issues.map(i => `<span class="issue-tag">${i}</span>`).join('')
    : '<span class="issue-tag" style="color:var(--text3)">정보 없음</span>'

  container.innerHTML = `
    ${company_name ? `<div class="company-name">${company_name}</div>` : ''}
    ${overview ? `<p class="overview-text">${overview}</p>` : ''}

    <div class="case-grid">
      <div class="case-box bull">
        <div class="case-label">📈 Bull Case</div>
        <ul class="case-list">${bullItems}</ul>
      </div>
      <div class="case-box bear">
        <div class="case-label">📉 Bear Case</div>
        <ul class="case-list">${bearItems}</ul>
      </div>
    </div>

    ${key_issues.length ? `
      <div>
        <div style="font-size:12px;color:var(--text3);margin-bottom:8px;">주요 이슈</div>
        <div class="issue-tags">${issueTags}</div>
      </div>
    ` : ''}
  `
}
