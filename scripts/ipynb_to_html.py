#!/usr/bin/env python3
import argparse
import os
import sys
from collections.abc import Mapping

import nbformat
from nbconvert import HTMLExporter

WIDGET_STATE_MIMETYPE = "application/vnd.jupyter.widget-state+json"


def _normalize_widget_metadata(nb: nbformat.NotebookNode) -> None:
    """Ensure widget metadata matches what nbconvert expects."""
    widgets_meta = nb.metadata.get("widgets")
    if not isinstance(widgets_meta, Mapping):
        return

    state_bundle = widgets_meta.get(WIDGET_STATE_MIMETYPE)
    if not isinstance(state_bundle, Mapping):
        return
    if "state" in state_bundle:
        return

    # Copy widget states into the structure nbconvert's filter expects.
    raw_state = nbformat.from_dict(
        {
            key: value
            for key, value in state_bundle.items()
            if isinstance(value, Mapping)
        }
    )

    fixed_bundle = nbformat.from_dict({"state": raw_state})
    fixed_bundle.setdefault("version_major", state_bundle.get("version_major", 2))
    fixed_bundle.setdefault("version_minor", state_bundle.get("version_minor", 0))

    widgets_meta[WIDGET_STATE_MIMETYPE] = fixed_bundle

def convert(ipynb_path: str, out_dir: str):
    if not os.path.isfile(ipynb_path):
        sys.exit(f"Error: “{ipynb_path}” does not exist or isn’t a file.")
    os.makedirs(out_dir, exist_ok=True)

    basename = os.path.splitext(os.path.basename(ipynb_path))[0]
    out_path = os.path.join(out_dir, f"{basename}.html")

    # load notebook, normalize widget metadata, and export to HTML
    nb = nbformat.read(ipynb_path, as_version=4)
    _normalize_widget_metadata(nb)
    html_exporter = HTMLExporter()
    body, _ = html_exporter.from_notebook_node(nb)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(body)

    print(f"✔ Converted → {out_path}")

def main():
    p = argparse.ArgumentParser(
        description="Convert a Jupyter .ipynb to HTML, preserving base filename."
    )
    p.add_argument(
        "--ipynb", "-i",
        required=True,
        help="path to the source .ipynb file"
    )
    p.add_argument(
        "--outdir", "-o",
        required=True,
        help="destination directory for the .html file"
    )
    args = p.parse_args()

    convert(args.ipynb, args.outdir)

if __name__ == "__main__":
    main()
