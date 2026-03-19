export function renderPerformanceWidget(container) {
  const stats = { rag: [], norag: [] }

  function avg(arr) {
    return arr.length ? Math.round(arr.reduce((a, b) => a + b, 0) / arr.length) : 0
  }

  function update() {
    const ragAvg = avg(stats.rag)
    const noragAvg = avg(stats.norag)
    const maxMs = Math.max(ragAvg, noragAvg, 1)
    const ragPct = Math.round((ragAvg / maxMs) * 100)
    const noragPct = Math.round((noragAvg / maxMs) * 100)

    const ragCount = stats.rag.length
    const noragCount = stats.norag.length

    container.innerHTML = `
      <div class="perf-grid">
        <div class="perf-stat">
          <div class="perf-stat-label">⚡ RAG 평균 응답</div>
          <div class="perf-stat-value" style="color:var(--accent)">${ragAvg || '—'}</div>
          <div class="perf-stat-unit">${ragAvg ? 'ms · ' + ragCount + '회' : '아직 없음'}</div>
        </div>
        <div class="perf-stat">
          <div class="perf-stat-label">📄 비RAG 평균 응답</div>
          <div class="perf-stat-value" style="color:var(--accent2)">${noragAvg || '—'}</div>
          <div class="perf-stat-unit">${noragAvg ? 'ms · ' + noragCount + '회' : '아직 없음'}</div>
        </div>
      </div>

      <div class="perf-bar-wrap" style="margin-top:16px;">
        <div class="perf-bar-label">
          <span>⚡ RAG</span>
          <span>${ragAvg ? ragAvg + 'ms' : '—'}</span>
        </div>
        <div class="perf-bar-bg">
          <div class="perf-bar-fill rag" style="width:${ragAvg ? ragPct : 0}%"></div>
        </div>
        <div class="perf-bar-label">
          <span>📄 비RAG</span>
          <span>${noragAvg ? noragAvg + 'ms' : '—'}</span>
        </div>
        <div class="perf-bar-bg">
          <div class="perf-bar-fill norag" style="width:${noragAvg ? noragPct : 0}%"></div>
        </div>
      </div>

      ${ragAvg && noragAvg ? `
        <div style="font-size:12px;color:var(--text3);margin-top:12px;text-align:center;">
          ${ragAvg < noragAvg
            ? `⚡ RAG가 ${noragAvg - ragAvg}ms 더 빠름`
            : `📄 비RAG가 ${ragAvg - noragAvg}ms 더 빠름`}
        </div>
      ` : `
        <div style="font-size:12px;color:var(--text3);margin-top:12px;text-align:center;">
          RAG와 비RAG 모드로 각각 질문하면 비교 결과가 표시됩니다
        </div>
      `}
    `
  }

  update()

  return {
    addResult(mode, latency_ms) {
      stats[mode].push(latency_ms)
      update()
    }
  }
}
