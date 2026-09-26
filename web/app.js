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
const brandingSlides = document.getElementById('branding-slides');
const brandingVideo = document.getElementById('branding-video');
const brandingPrevious = document.getElementById('branding-previous');
const brandingNext = document.getElementById('branding-next');
const brandingCount = document.getElementById('branding-count');
const brandingDots = [...document.querySelectorAll('#branding-dots button')];
const brandingOverlay = document.getElementById('branding-overlay');
const brandingClose = document.getElementById('branding-close');
const pageShell = document.getElementById('page-shell');

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
      startBrandCycle(3000);
    }, names.length * 2500);
  }, delay);
}

const brandingSlideCount = brandingSlides.children.length;
let activeBrandingSlide = 0;
let brandingScrollFrame = 0;
let brandingAutoTimer = 0;
let brandingInteracted = false;
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (reducedMotion) brandingVideo.poster = '/static/branding/branding-4-poster.png?v=desktop2';

function stopBrandingAutoplay() {
  brandingInteracted = true;
  window.clearTimeout(brandingAutoTimer);
}

function scheduleBrandingAdvance() {
  window.clearTimeout(brandingAutoTimer);
  if (brandingInteracted || reducedMotion || brandingOverlay.hidden || activeBrandingSlide >= brandingSlideCount - 1) return;
  brandingAutoTimer = window.setTimeout(() => goToBrandingSlide(activeBrandingSlide + 1), 4200);
}

function closeBranding() {
  window.clearTimeout(brandingAutoTimer);
  brandingVideo.pause();
  brandingOverlay.hidden = true;
  document.body.classList.remove('branding-open');
  pageShell.inert = false;
  heading.focus({ preventScroll: true });
}

function updateBrandingSlide() {
  const index = Math.max(0, Math.min(brandingSlideCount - 1, Math.round(brandingSlides.scrollLeft / brandingSlides.clientWidth)));
  if (index !== activeBrandingSlide) {
    activeBrandingSlide = index;
    if (index === brandingSlideCount - 1 && !reducedMotion) {
      brandingVideo.currentTime = 0;
      brandingVideo.play().catch(() => {});
    } else {
      brandingVideo.pause();
    }
    scheduleBrandingAdvance();
  }
  brandingCount.textContent = `${index + 1} / ${brandingSlideCount}`;
  brandingDots.forEach((dot, dotIndex) => {
    if (dotIndex === index) dot.setAttribute('aria-current', 'true');
    else dot.removeAttribute('aria-current');
  });
  brandingPrevious.disabled = index === 0;
  brandingNext.disabled = index === brandingSlideCount - 1;
}

function goToBrandingSlide(index) {
  const target = Math.max(0, Math.min(brandingSlideCount - 1, index));
  brandingSlides.scrollTo({
    left: target * brandingSlides.clientWidth,
    behavior: reducedMotion ? 'auto' : 'smooth',
  });
}

brandingClose.addEventListener('click', closeBranding);
brandingSlides.addEventListener('pointerdown', stopBrandingAutoplay);
brandingSlides.addEventListener('wheel', stopBrandingAutoplay, {passive: true});
brandingSlides.addEventListener('scroll', () => {
  window.cancelAnimationFrame(brandingScrollFrame);
  brandingScrollFrame = window.requestAnimationFrame(updateBrandingSlide);
});
brandingSlides.addEventListener('keydown', (event) => {
  if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
  event.preventDefault();
  stopBrandingAutoplay();
  goToBrandingSlide(activeBrandingSlide + (event.key === 'ArrowRight' ? 1 : -1));
});
brandingPrevious.addEventListener('click', () => { stopBrandingAutoplay(); goToBrandingSlide(activeBrandingSlide - 1); });
brandingNext.addEventListener('click', () => { stopBrandingAutoplay(); goToBrandingSlide(activeBrandingSlide + 1); });
brandingDots.forEach((dot, index) => dot.addEventListener('click', () => {
  stopBrandingAutoplay();
  goToBrandingSlide(index);
}));
brandingVideo.addEventListener('ended', closeBranding);
brandingVideo.addEventListener('click', () => {
  brandingVideo.currentTime = 0;
  brandingVideo.play().catch(() => {});
});
document.addEventListener('keydown', (event) => {
  if (brandingOverlay.hidden) return;
  if (event.key === 'Escape') { closeBranding(); return; }
  if (event.key !== 'Tab') return;
  const focusables = [brandingClose, brandingSlides, brandingPrevious, ...brandingDots, brandingNext];
  const current = focusables.indexOf(document.activeElement);
  if (event.shiftKey && current === 0) { event.preventDefault(); brandingNext.focus(); }
  if (!event.shiftKey && current === focusables.length - 1) { event.preventDefault(); brandingClose.focus(); }
});
document.addEventListener('visibilitychange', () => {
  if (document.hidden) brandingVideo.pause();
});
updateBrandingSlide();
scheduleBrandingAdvance();
brandingClose.focus();

convertButton.addEventListener('click', convertMarkdown);
retryButton.addEventListener('click', convertMarkdown);
downloadButton.addEventListener('click', downloadPdf);
uploadButton.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', loadMarkdownFile);
textarea.addEventListener('input', sourceChanged);
previewLink.addEventListener('click', showPreview);
startBrandCycle();
