#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s <review-folder|review-range>\n' "$0" >&2
  printf 'Examples:\n' >&2
  printf '  %s 001-010\n' "$0" >&2
  printf '  %s reviews/001-010\n' "$0" >&2
  exit 1
fi

review_arg="${1%/}"

if [[ "$review_arg" =~ ^[0-9]{3}-[0-9]{3}$ ]]; then
  review_dir="reviews/$review_arg"
else
  review_dir="$review_arg"
fi

if [ ! -d "$review_dir" ]; then
  printf 'Error: review folder not found: %s\n' "$review_dir" >&2
  exit 1
fi

if [ ! -f "$review_dir/test.yaml" ]; then
  printf 'Error: missing %s/test.yaml\n' "$review_dir" >&2
  exit 1
fi

review_name="revisao-$(basename "$review_dir")"
review_input="$(realpath --relative-to=templates "$review_dir")"
out_dir="output/pdf/$review_name"

mkdir -p "$out_dir"

typst compile --root . templates/test.typ "$out_dir/test.pdf" --input topic="$review_input"

printf 'Compiled review test to %s\n' "$out_dir/test.pdf"
