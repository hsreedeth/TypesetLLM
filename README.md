# GPT to Publication: Professional PDF Orchestrator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/hsreedeth/GPTnotesToPublicationStylePDF)

**Bridging the gap between AI-driven brainstorming and academic-grade typesetting.**

LLMs like GPT-4 are incredible for drafting ideas, but their raw outputs are often unformatted, lacks structured bibliographies, and doesn't meet the rigorous standards of journals (IEEE, ACM, etc.). This repository provides a robust pipeline to transform raw GPT-generated notes into publication-ready, beautifully typeset PDFs.

## 🚀 Key Features

*   **Intelligent Parsing**: Automatically detects mathematical notation, code blocks, and hierarchical structures from LLM exports.
*   **LaTeX Integration**: Seamless conversion to .tex files with pre-configured templates for IEEE, ACM, and generic scientific papers.
*   **Bibliography Support**: Simple workflows for merging BibTeX citations with your AI-drafted content.
*   **Customizable Theming**: Toggle between "Journal Style", "Modern Technical Report", and "Clean Draft" modes.

## 🛠️ Installation

Ensure you have a TeX distribution (like TeX Live or MiKTeX) and Python 3.8+ installed.

```bash
# Clone the repository
git clone https://github.com/hsreedeth/GPTnotesToPublicationStylePDF.git
cd GPTnotesToPublicationStylePDF

# Install dependencies
pip install -r requirements.txt
```

## 🔄 The Workflow

1.  **Draft**: Generate your technical content using your favorite LLM.
2.  **Export**: Save the chat or output as a `.txt` or `.md` file in the `input/` directory.
3.  **Process**: Run the conversion script:
    ```bash
    python orchestrator.py --input my_notes.md --style ieee
    ```
4.  **Polish**: The script generates a `.tex` project. Open it in Overleaf or your local TeX editor for final manual tweaks.
5.  **Compile**: Generate your high-resolution PDF.

## 📖 Usage Examples

### Converting a Markdown Note
To convert a raw markdown export into a two-column IEEE style paper:
```bash
python converter.py --src data/raw_notes.md --template ieee_2column --out research_paper.pdf
```

### Customizing Math Rendering
This tool ensures that GPT's LaTeX-style math (e.g., `\( E=mc^2 \)`) is correctly escaped and wrapped in appropriate LaTeX environments for the target template.

## 🤝 Contributing

We welcome contributions from researchers and developers! 
- **Bug Reports**: Open an issue if the parser misses specific GPT formatting patterns.
- **New Templates**: Submit a PR with a new LaTeX template (e.g., Nature, Springer).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Developed with ❤️ for the research community.*
