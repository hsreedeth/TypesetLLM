const textarea = document.getElementById('markdown-input');
const fileInput = document.getElementById('file-input');
const uploadButton = document.getElementById('upload-button');
const convertButton = document.getElementById('convert-button');
const downloadButton = document.getElementById('download-button');
const retryButton = document.getElementById('retry-button');
const statusPanel = document.getElementById('status-panel');
const statusMessage = document.getElementById('status-message');
const resultActions = document.getElementById('result-actions');
const warnings = document.getElementById('warnings');
const preview = document.getElementById('pdf-preview');
const previewLink = document.getElementById('preview-link');
const heading = document.getElementById('brand-heading');
const suffix = document.getElementById('brand-suffix');

let pdfBlobUrl = null;
let pdfFilename = 'converted_document.pdf';
let sourceRevision = 0;
let activeRequest = null;

function setPanelState(state, message = '') {
  statusPanel.className = `panel-button panel-status panel-status-${state}`;
  statusMessage.textContent = message;
}

function clearResult() {
  if (pdfBlobUrl) URL.revokeObjectURL(pdfBlobUrl);
  pdfBlobUrl = null;
  downloadButton.disabled = true;
  resultActions.classList.remove('visible');
  preview.classList.remove('visible');
  preview.removeAttribute('src');
  warnings.textContent = '';
}

function sourceChanged() {
  sourceRevision += 1;
  if (activeRequest) activeRequest.abort();
  activeRequest = null;
  clearResult();
  setPanelState('idle');
}

function responseFilename(response) {
  const disposition = response.headers.get('Content-Disposition') || '';
  const match = disposition.match(/filename\*?=(?:UTF-8''|["']?)([^"';]+)/i);
  return match ? decodeURIComponent(match[1]) : 'converted_document.pdf';
}

async function convertMarkdown() {
  const markdownText = textarea.value;
  if (!markdownText.trim()) {
    clearResult();
    setPanelState('error', 'Paste or upload Markdown first.');
    return;
  }

  clearResult();
  setPanelState('loading');
  const revision = sourceRevision;
  const controller = new AbortController();
  activeRequest = controller;

  try {
    const response = await fetch('/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ markdown_text: markdownText }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      const detail = payload.detail || {};
      const message = typeof detail === 'object' ? detail.message : detail;
      const reference = detail.reference ? ` Reference: ${detail.reference}` : '';
      throw new Error(`${message || 'Could not generate PDF.'}${reference}`);
    }

    const blob = await response.blob();
    if (revision !== sourceRevision || controller.signal.aborted) return;
    pdfBlobUrl = URL.createObjectURL(blob);
    pdfFilename = responseFilename(response);
    downloadButton.disabled = false;
    resultActions.classList.add('visible');
    setPanelState('success', 'PDF ready');
    try {
      const notices = JSON.parse(response.headers.get('X-Typeset-Warnings') || '[]');
      warnings.textContent = notices.join('\n');
    } catch (_) {
      warnings.textContent = 'Review the PDF preview before downloading.';
    }
  } catch (error) {
    if (revision !== sourceRevision || controller.signal.aborted) return;
    setPanelState('error', error.message || 'Could not generate PDF.');
    resultActions.classList.add('visible');
  } finally {
    if (activeRequest === controller) activeRequest = null;
  }
}

function downloadPdf() {
  if (!pdfBlobUrl) return;
  const link = document.createElement('a');
  link.href = pdfBlobUrl;
  link.download = pdfFilename;
  document.body.appendChild(link);
  link.click();
  link.remove();
}

async function loadMarkdownFile() {
  const file = fileInput.files && fileInput.files[0];
  if (!file) return;
  if (file.size > 1024 * 1024) {
    setPanelState('error', 'Markdown files must be under 1 MB.');
    fileInput.value = '';
    return;
  }
  const content = await file.text();
  textarea.value = content;
  sourceChanged();
  textarea.focus();
  fileInput.value = '';
}

function showPreview(event) {
  event.preventDefault();
  if (!pdfBlobUrl) return;
  preview.src = `${pdfBlobUrl}#toolbar=0`;
  preview.classList.add('visible');
  preview.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function animateSuffix(next) {
  suffix.classList.remove('enter');
  suffix.classList.add('exit');
  window.setTimeout(() => {
    suffix.textContent = next;
    heading.setAttribute('aria-label', `Typeset${next}`);
    suffix.classList.remove('exit');
    suffix.classList.add('enter');
  }, 350);
}

function startBrandCycle(delay = 10000) {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  window.setTimeout(() => {
    const names = ['ChatGPT', 'Claude', 'Gemini', 'Kimi.ai', 'DeepSeek', 'LLM'];
    names.forEach((name, index) => window.setTimeout(() => animateSuffix(name), index * 2500));
    window.setTimeout(() => {
      startBrandCycle(15000);
    }, names.length * 2500);
  }, delay);
}

convertButton.addEventListener('click', convertMarkdown);
retryButton.addEventListener('click', convertMarkdown);
downloadButton.addEventListener('click', downloadPdf);
uploadButton.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', loadMarkdownFile);
textarea.addEventListener('input', sourceChanged);
previewLink.addEventListener('click', showPreview);
startBrandCycle();
