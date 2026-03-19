import { renderUploadPanel } from './components/UploadPanel.js'
import { renderAnalysisCard } from './components/AnalysisCard.js'
import { renderMetricsTable } from './components/MetricsTable.js'
import { renderQAPanel } from './components/QAPanel.js'
import { renderPerformanceWidget } from './components/PerformanceWidget.js'

// Mount upload panel
const uploadPanelEl = document.getElementById('upload-panel')
renderUploadPanel(uploadPanelEl, onDocumentReady)

function onDocumentReady({ document_id, analysis }) {
  // Show main content
  document.getElementById('main-content').classList.remove('hidden')

  // Render analysis
  renderAnalysisCard(document.getElementById('analysis-panel'), analysis)

  // Render financials
  renderMetricsTable(document.getElementById('metrics-panel'), analysis?.financials)

  // Render performance widget first (returns controller)
  const perfWidget = renderPerformanceWidget(document.getElementById('perf-panel'))

  // Render Q&A panel with callback to update perf widget
  renderQAPanel(
    document.getElementById('qa-panel'),
    document_id,
    (result) => perfWidget.addResult(result.mode, result.latency_ms)
  )

  // Smooth scroll to main content
  document.getElementById('main-content').scrollIntoView({ behavior: 'smooth' })
}
