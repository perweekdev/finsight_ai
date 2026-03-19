import { uploadPDF, analyzeDocument } from '../api.js'

export function renderUploadPanel(container, onComplete) {
  container.innerHTML = `
    <div class="upload-zone" id="drop-zone">
      <div class="upload-icon">📄</div>
      <div class="upload-title">PDF 파일을 드래그하거나 클릭하여 업로드</div>
      <div class="upload-sub">증권사 리포트, DART 공시 등 금융 PDF 지원</div>
      <input type="file" class="upload-input" id="file-input" accept=".pdf" />
    </div>
    <div class="status-bar hidden" id="status-bar">
      <span id="status-icon"></span>
      <span id="status-text"></span>
    </div>
  `

  const zone = container.querySelector('#drop-zone')
  const fileInput = container.querySelector('#file-input')
  const statusBar = container.querySelector('#status-bar')
  const statusIcon = container.querySelector('#status-icon')
  const statusText = container.querySelector('#status-text')

  function setStatus(state, icon, text) {
    statusBar.classList.remove('hidden', 'success', 'error')
    if (state) statusBar.classList.add(state)
    statusIcon.innerHTML = icon
    statusText.textContent = text
  }

  async function handleFile(file) {
    if (!file || !file.name.endsWith('.pdf')) {
      setStatus('error', '⚠️', 'PDF 파일만 업로드 가능합니다.')
      return
    }

    zone.style.pointerEvents = 'none'
    setStatus('', '<span class="spinner"></span>', `"${file.name}" 업로드 중...`)

    try {
      const uploadData = await uploadPDF(file)
      const { document_id, filename, pages, chunks } = uploadData
      setStatus('', '<span class="spinner"></span>', `파싱 완료 (${pages}페이지, ${chunks}청크) — 기업 분석 중...`)

      const analyzeData = await analyzeDocument(document_id)
      const company = analyzeData.analysis?.company_name || filename
      setStatus('success', '✅', `분석 완료: ${company} · ${pages}p · ${chunks}청크`)

      onComplete({ document_id, filename, pages, chunks, analysis: analyzeData.analysis })
    } catch (err) {
      setStatus('error', '❌', `오류: ${err.message}`)
      zone.style.pointerEvents = 'auto'
    }
  }

  zone.addEventListener('click', () => fileInput.click())
  fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]))
  zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('drag-over') })
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'))
  zone.addEventListener('drop', (e) => {
    e.preventDefault()
    zone.classList.remove('drag-over')
    handleFile(e.dataTransfer.files[0])
  })
}
