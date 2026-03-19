// 백엔드 API 호출 모듈
const BASE_URL = import.meta.env.VITE_API_URL || '/api'

export async function uploadPDF(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE_URL}/upload`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function analyzeDocument(documentId) {
  const res = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id: documentId }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function askQuestion(documentId, question, mode) {
  const res = await fetch(`${BASE_URL}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ document_id: documentId, question, mode }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
