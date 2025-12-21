#!/bin/bash

# --- Simple Markdown to PDF Converter ---

# 1. Check if an input file was provided
if [ -z "$1" ]; then
  echo "Error: No input .md file supplied."
  echo "Usage: ./convert.sh <path/to/file.md>"
  exit 1
fi

# 2. Define file paths
INPUT_FILE="$1"
OUTPUT_DIR="out"

# Get just the filename (e.g., "MAIP_protocol.md")
FILENAME=$(basename "$INPUT_FILE")

# Get the filename without the .md extension (e.g., "MAIP_protocol")
FILENAME_NO_EXT="${FILENAME%.md}"

# Create the final output path
OUTPUT_FILE="${OUTPUT_DIR}/${FILENAME_NO_EXT}.pdf"

# 3. Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# 4. Run the conversion command
echo "Converting ${INPUT_FILE}..."
python -m src.cli "$INPUT_FILE" -o "$OUTPUT_FILE"

echo "✅ Done. Output saved to ${OUTPUT_FILE}"