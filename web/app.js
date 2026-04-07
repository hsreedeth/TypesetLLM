const textarea = document.getElementById("markdown-input");
const convertButton = document.getElementById("convert-button");
const downloadButton = document.getElementById("download-button");
const statusPanel = document.getElementById("status-panel");
const statusMessage = document.getElementById("status-message");

let pdfBlobUrl = null;

function setPanelState(state, message = "") {
  statusPanel.className = `panel-button panel-status panel-status-${state}`;
  statusMessage.textContent = message;
}

function clearPdfUrl() {
  if (pdfBlobUrl) {
    URL.revokeObjectURL(pdfBlobUrl);
    pdfBlobUrl = null;
  }
}

function setDownloadEnabled(enabled) {
  downloadButton.disabled = !enabled;
  downloadButton.classList.toggle("action-button-muted", !enabled);
}

function resetToIdle() {
  clearPdfUrl();
  setPanelState("idle");
  setDownloadEnabled(false);
}

async function convertMarkdown() {
  const markdownText = textarea.value.trim();

  if (!markdownText) {
    setPanelState("error", "Paste markdown first.");
    setDownloadEnabled(false);
    return;
  }

  clearPdfUrl();
  setPanelState("loading");
  setDownloadEnabled(false);

  try {
    const response = await fetch("/convert", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        markdown_text: markdownText,
      }),
    });

    if (!response.ok) {
      throw new Error("Conversion failed.");
    }

    const blob = await response.blob();
    pdfBlobUrl = URL.createObjectURL(blob);
    setPanelState("success", "Converted to PDF!");
    setDownloadEnabled(true);
  } catch (error) {
    setPanelState("error", "Could not generate PDF.");
    setDownloadEnabled(false);
  }
}

function downloadPdf() {
  if (!pdfBlobUrl) {
    return;
  }

  const link = document.createElement("a");
  link.href = pdfBlobUrl;
  link.download = "converted_document.pdf";
  document.body.appendChild(link);
  link.click();
  link.remove();
}

convertButton.addEventListener("click", convertMarkdown);
downloadButton.addEventListener("click", downloadPdf);
textarea.addEventListener("input", () => {
  if (statusPanel.classList.contains("panel-status-loading")) {
    return;
  }
  resetToIdle();
});
