import { askQuestion } from '../api.js'

export function renderQAPanel(container, documentId, onResult) {
  let currentMode = 'rag'

  container.innerHTML = `
    <div class="mode-toggle">
      <button class="mode-btn active" id="btn-rag">⚡ RAG (벡터 검색)</button>
      <button class="mode-btn" id="btn-norag">📄 비RAG (전문 컨텍스트)</button>
    </div>
    <div class="question-form">
      <input
        class="question-input"
        id="question-input"
        type="text"
        placeholder="질문을 입력하세요 (예: 이 기업의 주요 리스크는?)"
      />
      <button class="ask-btn" id="ask-btn">질문하기</button>
    </div>
    <div id="answer-area">
      <div class="answer-box">
        <span class="answer-empty">질문을 입력하면 답변이 여기에 표시됩니다.</span>
      </div>
    </div>
  `

  const btnRag = container.querySelector('#btn-rag')
  const btnNoRag = container.querySelector('#btn-norag')
  const input = container.querySelector('#question-input')
  const askBtn = container.querySelector('#ask-btn')
  const answerArea = container.querySelector('#answer-area')

  function setMode(mode) {
    currentMode = mode
    btnRag.classList.toggle('active', mode === 'rag')
    btnNoRag.classList.toggle('active', mode === 'norag')
  }

  function renderAnswer(result) {
    const { answer, sources = [], mode, latency_ms, model } = result
    const sourcesHtml = mode === 'rag' && sources.length ? `
      <div class="sources-list">
        <div style="font-size:11px;color:var(--text3);margin-bottom:6px;">📎 출처 청크 (${sources.length}개)</div>
        ${sources.map(s => `
          <div class="source-item">
            <div class="source-meta">
              <span>청크 ${s.index}</span>
              <span class="similarity-badge">유사도 ${(s.similarity * 100).toFixed(1)}%</span>
            </div>
            <div>${s.content}</div>
          </div>
        `).join('')}
      </div>
    ` : ''

    answerArea.innerHTML = `
      <div class="answer-box">${answer}</div>
      <div class="mt8">
        <span class="latency-tag">⏱ ${latency_ms}ms</span>
        <span class="latency-tag" style="margin-left:6px;">${mode === 'rag' ? '⚡ RAG' : '📄 비RAG'}</span>
        <span class="latency-tag" style="margin-left:6px;">🤖 ${model}</span>
      </div>
      ${sourcesHtml}
    `
  }

  async function handleAsk() {
    const question = input.value.trim()
    if (!question) return

    askBtn.disabled = true
    askBtn.textContent = '...'
    answerArea.innerHTML = `
      <div class="answer-box">
        <span class="answer-empty"><span class="spinner"></span> 답변 생성 중...</span>
      </div>
    `

    try {
      const result = await askQuestion(documentId, question, currentMode)
      renderAnswer(result)
      onResult(result)
    } catch (err) {
      answerArea.innerHTML = `<div class="answer-box" style="color:var(--red)">오류: ${err.message}</div>`
    } finally {
      askBtn.disabled = false
      askBtn.textContent = '질문하기'
    }
  }

  btnRag.addEventListener('click', () => setMode('rag'))
  btnNoRag.addEventListener('click', () => setMode('norag'))
  askBtn.addEventListener('click', handleAsk)
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') handleAsk() })
}
