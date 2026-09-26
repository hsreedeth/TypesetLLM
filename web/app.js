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
const watchSlidesButton = document.getElementById('watch-slides-button');
const brandingSlides = document.getElementById('branding-slides');
const brandingVideo = document.getElementById('branding-video');
const introVideo = document.getElementById('intro-video');
const brandingCount = document.getElementById('branding-count');
const brandingDots = [...document.querySelectorAll('#branding-dots button')];
const brandingOverlay = document.getElementById('branding-overlay');
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
let brandingScrollSettleTimer = 0;
let brandingAutoTimer = 0;
let introFallbackTimer = 0;
let brandingInteracted = false;
let brandingReturnFocus = heading;
let brandingTouchStart = null;
let downwardWheelDistance = 0;
let wheelResetTimer = 0;
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (reducedMotion) {
  brandingVideo.poster = '/static/branding/branding-4-poster.png?v=desktop2';
  introVideo.poster = '/static/branding/branding-4-poster.png?v=desktop2';
}

function stopBrandingAutoplay() {
  brandingInteracted = true;
  window.clearTimeout(brandingAutoTimer);
}

function scheduleBrandingAdvance() {
  window.clearTimeout(brandingAutoTimer);
  if (brandingInteracted || reducedMotion || brandingOverlay.hidden || brandingOverlay.classList.contains('intro-only') || activeBrandingSlide >= brandingSlideCount - 1) return;
  brandingAutoTimer = window.setTimeout(() => goToBrandingSlide(activeBrandingSlide + 1), 4200);
}

function closeBranding() {
  if (brandingOverlay.hidden) return;
  window.clearTimeout(brandingAutoTimer);
  window.clearTimeout(introFallbackTimer);
  window.clearTimeout(wheelResetTimer);
  window.clearTimeout(brandingScrollSettleTimer);
  downwardWheelDistance = 0;
  brandingTouchStart = null;
  introVideo.pause();
  brandingVideo.pause();
  brandingOverlay.hidden = true;
  document.body.classList.remove('branding-open');
  pageShell.inert = false;
  brandingReturnFocus.focus({ preventScroll: true });
  brandingReturnFocus = heading;
}

function finishIntro() {
  if (brandingOverlay.classList.contains('intro-only')) closeBranding();
}

function openBrandingSlides() {
  window.clearTimeout(introFallbackTimer);
  downwardWheelDistance = 0;
  brandingTouchStart = null;
  introVideo.pause();
  brandingVideo.pause();
  brandingVideo.parentElement.classList.remove('is-playing');
  brandingVideo.currentTime = 0;
  brandingVideo.load();
  brandingInteracted = false;
  brandingReturnFocus = watchSlidesButton;
  brandingOverlay.classList.remove('intro-only');
  brandingOverlay.hidden = false;
  document.body.classList.add('branding-open');
  pageShell.inert = true;
  brandingSlides.scrollLeft = 0;
  activeBrandingSlide = 0;
  updateBrandingSlide();
  scheduleBrandingAdvance();
  brandingSlides.focus({ preventScroll: true });
}

function updateBrandingSlide() {
  if (brandingOverlay.hidden || brandingOverlay.classList.contains('intro-only')) return;
  const index = Math.max(0, Math.min(brandingSlideCount - 1, Math.round(brandingSlides.scrollLeft / brandingSlides.clientWidth)));
  if (index !== activeBrandingSlide) {
    activeBrandingSlide = index;
    brandingVideo.pause();
    scheduleBrandingAdvance();
  }
  brandingCount.textContent = `${index + 1} / ${brandingSlideCount}`;
  brandingDots.forEach((dot, dotIndex) => {
    if (dotIndex === index) dot.setAttribute('aria-current', 'true');
    else dot.removeAttribute('aria-current');
  });
}

function settleBrandingSlide() {
  if (brandingOverlay.hidden || brandingOverlay.classList.contains('intro-only')) return;
  updateBrandingSlide();
  if (activeBrandingSlide !== brandingSlideCount - 1 || reducedMotion) return;
  brandingVideo.parentElement.classList.remove('is-playing');
  brandingVideo.currentTime = 0;
  brandingVideo.play().catch(() => {
    // The poster remains visible if a mobile browser still requires a gesture.
  });
}

function goToBrandingSlide(index) {
  const target = Math.max(0, Math.min(brandingSlideCount - 1, index));
  brandingSlides.scrollTo({
    left: target * brandingSlides.clientWidth,
    behavior: reducedMotion ? 'auto' : 'smooth',
  });
}

watchSlidesButton.addEventListener('click', openBrandingSlides);
introVideo.addEventListener('ended', finishIntro);
introVideo.addEventListener('error', finishIntro);
brandingSlides.addEventListener('pointerdown', stopBrandingAutoplay);
brandingSlides.addEventListener('wheel', (event) => {
  if (brandingOverlay.classList.contains('intro-only')) return;
  stopBrandingAutoplay();
  if (event.deltaY <= 0 || event.deltaY <= Math.abs(event.deltaX) * 1.4) {
    downwardWheelDistance = 0;
    return;
  }
  downwardWheelDistance += event.deltaY;
  window.clearTimeout(wheelResetTimer);
  wheelResetTimer = window.setTimeout(() => { downwardWheelDistance = 0; }, 500);
  if (downwardWheelDistance > 100) closeBranding();
}, {passive: true});
brandingOverlay.addEventListener('touchstart', (event) => {
  brandingTouchStart = !brandingOverlay.classList.contains('intro-only') && event.touches.length === 1
    ? { x: event.touches[0].clientX, y: event.touches[0].clientY }
    : null;
}, {passive: true});
brandingOverlay.addEventListener('touchend', (event) => {
  if (!brandingTouchStart || brandingOverlay.hidden || brandingOverlay.classList.contains('intro-only')) return;
  const deltaX = event.changedTouches[0].clientX - brandingTouchStart.x;
  const deltaY = event.changedTouches[0].clientY - brandingTouchStart.y;
  brandingTouchStart = null;
  if (deltaY > 80 && deltaY > Math.abs(deltaX) * 1.4) closeBranding();
}, {passive: true});
brandingOverlay.addEventListener('touchcancel', () => { brandingTouchStart = null; }, {passive: true});
brandingSlides.addEventListener('scroll', () => {
  window.cancelAnimationFrame(brandingScrollFrame);
  brandingScrollFrame = window.requestAnimationFrame(updateBrandingSlide);
  window.clearTimeout(brandingScrollSettleTimer);
  brandingScrollSettleTimer = window.setTimeout(settleBrandingSlide, 140);
});
brandingSlides.addEventListener('scrollend', () => {
  window.clearTimeout(brandingScrollSettleTimer);
  settleBrandingSlide();
});
brandingSlides.addEventListener('keydown', (event) => {
  if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
  event.preventDefault();
  stopBrandingAutoplay();
  goToBrandingSlide(activeBrandingSlide + (event.key === 'ArrowRight' ? 1 : -1));
});
brandingDots.forEach((dot, index) => dot.addEventListener('click', () => {
  stopBrandingAutoplay();
  goToBrandingSlide(index);
}));
brandingVideo.addEventListener('ended', closeBranding);
brandingVideo.addEventListener('playing', () => {
  brandingVideo.parentElement.classList.add('is-playing');
});
brandingVideo.addEventListener('error', () => {
  brandingVideo.parentElement.classList.remove('is-playing');
});
brandingVideo.addEventListener('click', () => {
  brandingVideo.parentElement.classList.remove('is-playing');
  brandingVideo.currentTime = 0;
  brandingVideo.play().catch(() => {});
});
document.addEventListener('keydown', (event) => {
  if (brandingOverlay.hidden) return;
  if (event.key === 'Escape') { closeBranding(); return; }
  if (event.key !== 'Tab') return;
  if (brandingOverlay.classList.contains('intro-only')) { event.preventDefault(); return; }
  const focusables = [brandingSlides, ...brandingDots];
  const current = focusables.indexOf(document.activeElement);
  if (event.shiftKey && current === 0) { event.preventDefault(); focusables[focusables.length - 1].focus(); }
  if (!event.shiftKey && current === focusables.length - 1) { event.preventDefault(); brandingSlides.focus(); }
});
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    introVideo.pause();
    brandingVideo.pause();
  } else if (!brandingOverlay.hidden && brandingOverlay.classList.contains('intro-only') && !reducedMotion) {
    introVideo.play().catch(finishIntro);
  }
});
if (reducedMotion) {
  introFallbackTimer = window.setTimeout(finishIntro, 1500);
} else {
  introVideo.play().catch(finishIntro);
}

convertButton.addEventListener('click', convertMarkdown);
retryButton.addEventListener('click', convertMarkdown);
downloadButton.addEventListener('click', downloadPdf);
uploadButton.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', loadMarkdownFile);
textarea.addEventListener('input', sourceChanged);
previewLink.addEventListener('click', showPreview);
startBrandCycle();
