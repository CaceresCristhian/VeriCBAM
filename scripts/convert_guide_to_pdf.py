#!/usr/bin/env python3
"""
Converts docs/TAB_7_EMPIRICAL_BENCHMARK_GUIDE.md into a high-fidelity,
publication-grade PDF document using Pandoc (with MathJax) and Microsoft Edge Headless.
"""

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


def build_pdf():
    repo_root = Path(__file__).resolve().parents[1]
    md_file = repo_root / "docs" / "TAB_7_EMPIRICAL_BENCHMARK_GUIDE.md"
    html_file = repo_root / "docs" / "TAB_7_EMPIRICAL_BENCHMARK_GUIDE_rendered.html"
    pdf_file = repo_root / "docs" / "TAB_7_EMPIRICAL_BENCHMARK_GUIDE.pdf"

    pandoc_exe = r"C:\Program Files\Pandoc\pandoc.EXE"
    edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    if not Path(pandoc_exe).exists():
        pandoc_exe = shutil.which("pandoc")
    if not Path(edge_exe).exists():
        edge_exe = shutil.which("msedge")

    if not pandoc_exe or not Path(pandoc_exe).exists():
        raise RuntimeError("Pandoc executable not found.")
    if not edge_exe or not Path(edge_exe).exists():
        raise RuntimeError("Microsoft Edge executable not found.")

    print(f"[1/4] Reading Markdown: {md_file.name}")
    md_content = md_file.read_text(encoding="utf-8")

    # Custom Pandoc HTML generation with MathJax
    print(f"[2/4] Generating styled HTML via Pandoc...")
    raw_html_tmp = repo_root / "docs" / "temp_raw.html"
    
    cmd_pandoc = [
        str(pandoc_exe),
        str(md_file),
        "-s",
        "--mathjax=https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml-full.js",
        "-o",
        str(raw_html_tmp),
    ]
    subprocess.run(cmd_pandoc, check=True)
    raw_html = raw_html_tmp.read_text(encoding="utf-8")
    if raw_html_tmp.exists():
        raw_html_tmp.unlink()

    # Inject Academic / Executive Publication CSS
    custom_css = """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

      @page {
        size: A4;
        margin: 18mm 16mm 18mm 16mm;
      }

      * {
        box-sizing: border-box;
      }

      body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 9.8pt;
        line-height: 1.55;
        color: #1e293b;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
        text-rendering: optimizeLegibility;
      }

      /* Title Banner / Header Block */
      h1:first-of-type {
        font-size: 18pt;
        font-weight: 800;
        color: #0f172a;
        margin-top: 0;
        margin-bottom: 6px;
        line-height: 1.25;
        border-bottom: 2px solid #2563eb;
        padding-bottom: 10px;
      }

      /* Headings */
      h2 {
        font-size: 13pt;
        font-weight: 700;
        color: #1e3a8a;
        margin-top: 22px;
        margin-bottom: 8px;
        padding-bottom: 4px;
        border-bottom: 1px solid #e2e8f0;
        page-break-after: avoid;
      }

      h3 {
        font-size: 10.8pt;
        font-weight: 700;
        color: #0f172a;
        margin-top: 14px;
        margin-bottom: 6px;
        page-break-after: avoid;
      }

      p {
        margin: 6px 0;
      }

      ul, ol {
        margin: 6px 0 10px 18px;
        padding-left: 6px;
      }

      li {
        margin-bottom: 4px;
      }

      strong {
        font-weight: 600;
        color: #0f172a;
      }

      hr {
        border: 0;
        height: 1px;
        background: #e2e8f0;
        margin: 16px 0;
      }

      /* Tables */
      table {
        width: 100% !important;
        border-collapse: collapse;
        margin: 12px 0 16px 0;
        font-size: 8.5pt;
        line-height: 1.35;
        page-break-inside: avoid;
      }

      th {
        background-color: #0f172a !important;
        color: #ffffff !important;
        font-weight: 600;
        text-align: left;
        padding: 7px 9px;
        border: 1px solid #0f172a;
      }

      td {
        padding: 6px 8px;
        border: 1px solid #cbd5e1;
        vertical-align: top;
      }

      tr:nth-child(even) {
        background-color: #f8fafc;
      }

      tr:hover {
        background-color: #f1f5f9;
      }

      /* Code / Monospace */
      code {
        font-family: 'JetBrains Mono', Consolas, "Courier New", monospace;
        font-size: 8.5pt;
        background-color: #f1f5f9;
        color: #0f172a;
        padding: 1px 4px;
        border-radius: 4px;
        border: 1px solid #e2e8f0;
      }

      pre {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 10px 14px;
        font-family: 'JetBrains Mono', Consolas, "Courier New", monospace;
        font-size: 8pt;
        line-height: 1.35;
        overflow-x: auto;
        page-break-inside: avoid;
        margin: 10px 0;
      }

      pre code {
        background-color: transparent !important;
        color: inherit !important;
        padding: 0;
        border: none;
        font-size: inherit;
      }

      /* Callout Boxes (GitHub-style Blockquotes) */
      blockquote {
        margin: 10px 0;
        padding: 8px 14px;
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        border-radius: 0 6px 6px 0;
        font-size: 9pt;
        color: #1e3a8a;
      }

      blockquote p {
        margin: 2px 0;
      }

      /* MathJax Display Equations */
      .math.display {
        margin: 8px 0 !important;
        overflow-x: auto;
        text-align: center;
      }

      /* Footer Note */
      .report-footer {
        margin-top: 30px;
        padding-top: 10px;
        border-top: 1px solid #cbd5e1;
        font-size: 7.5pt;
        color: #64748b;
        text-align: center;
      }
    </style>
    """

    # Inject style before </head>
    if "</head>" in raw_html:
        styled_html = raw_html.replace("</head>", f"{custom_css}\n</head>")
    else:
        styled_html = f"{custom_css}\n{raw_html}"

    # Append report footer
    footer_html = """
    <div class="report-footer">
      VeriCBAM Audit Suite • European Commission CBAM Compliance Verification Framework •
      University of Europe for Applied Sciences (Berlin) • Confidential Decision Support Document
    </div>
    """
    if "</body>" in styled_html:
        styled_html = styled_html.replace("</body>", f"{footer_html}\n</body>")

    html_file.write_text(styled_html, encoding="utf-8")
    print(f"[3/4] Rendered HTML saved to: {html_file.name}")

    # Convert HTML to PDF via Edge Headless
    print(f"[4/4] Converting to PDF via Microsoft Edge Headless engine...")
    if pdf_file.exists():
        pdf_file.unlink()

    html_uri = html_file.resolve().as_uri()
    
    cmd_edge = [
        str(edge_exe),
        "--headless=new",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=5000",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_file.resolve()}",
        html_uri,
    ]

    subprocess.run(cmd_edge, check=True)

    # Wait briefly for file write lock release
    time.sleep(1)

    if pdf_file.exists() and pdf_file.stat().st_size > 0:
        size_kb = pdf_file.stat().st_size / 1024
        print(f"SUCCESS: PDF successfully generated at:\n  {pdf_file} ({size_kb:.1f} KB)")
        return str(pdf_file)
    else:
        raise RuntimeError(f"PDF creation failed or output file is empty: {pdf_file}")


if __name__ == "__main__":
    try:
        pdf_path = build_pdf()
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
