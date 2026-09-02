#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found. Install Python 3 and try again."
  read -r -p "Press Return to close..." _
  exit 1
fi

input_file="${1:-}"

if [[ -z "$input_file" ]]; then
  echo "Drag an .ics file into this Terminal window, then press Return."
  read -r input_file

  # Terminal may insert escaped spaces when a file is dragged into the window.
  input_file="${input_file#\"}"
  input_file="${input_file%\"}"
  input_file="${input_file#\'}"
  input_file="${input_file%\'}"
  input_file="${input_file//\\ / }"
  input_file="${input_file//\\(/(}"
  input_file="${input_file//\\)/)}"
  input_file="$(printf '%b' "$input_file")"
fi

if [[ ! -f "$input_file" ]]; then
  echo "File not found: $input_file"
  read -r -p "Press Return to close..." _
  exit 1
fi

case "$input_file" in
  *.ics|*.ICS) ;;
  *)
    echo "Please choose an iCalendar file with the .ics extension."
    read -r -p "Press Return to close..." _
    exit 1
    ;;
esac

input_dir="$(cd "$(dirname "$input_file")" && pwd)"
input_file="$input_dir/$(basename "$input_file")"
output_file="$SCRIPT_DIR/Weekly Timetable.md"

if [[ -e "$output_file" ]]; then
  read -r -p "Weekly Timetable.md already exists. Overwrite it? [y/N] " answer
  case "$answer" in
    y|Y|yes|YES) ;;
    *)
      echo "Cancelled."
      read -r -p "Press Return to close..." _
      exit 0
      ;;
  esac
fi

echo
echo "Generating the timetable..."
python3 "$SCRIPT_DIR/generate_timetable.py" "$input_file" -o "$output_file"

echo
echo "Done: $output_file"
open -R "$output_file" 2>/dev/null || true
read -r -p "Press Return to close..." _
