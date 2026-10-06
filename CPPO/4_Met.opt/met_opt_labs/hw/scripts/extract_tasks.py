#!/usr/bin/env python3
"""
Извлекает текст из PDF-файлов с заданиями в папке hw и сохраняет в hw/README_tasks.md
Скрипт берёт последние несколько страниц из каждого PDF (по умолчанию 4) — там обычно находятся домашние задания.
"""
from pathlib import Path
import fitz  # PyMuPDF
import sys


def extract_tail_text(pdf_path: Path, tail_pages: int = 4) -> str:
    doc = fitz.open(str(pdf_path))
    n = doc.page_count
    start = max(0, n - tail_pages)
    texts = []
    for i in range(start, n):
        page = doc.load_page(i)
        texts.append(page.get_text("text"))
    doc.close()
    return "\n\n".join(texts)


def main():
    script_dir = Path(__file__).resolve().parent
    hw_dir = script_dir.parent
    out_md = hw_dir / "README_tasks.md"

    pdfs = sorted([p for p in hw_dir.glob("*.pdf") if p.name.lower().startswith("hw_lab_")])
    if not pdfs:
        print("PDF-файлы hw_lab_*.pdf не найдены в", hw_dir)
        sys.exit(1)

    with out_md.open("w", encoding="utf-8") as f:
        f.write("# Извлечённые формулировки домашних заданий\n\n")
        for pdf in pdfs:
            print("Обработка:", pdf)
            text = extract_tail_text(pdf, tail_pages=6)
            f.write(f"## {pdf.name}\n\n")
            f.write("---\n\n")
            f.write(text)
            f.write("\n\n")

    print("Готово. Результат сохранён в", out_md)


if __name__ == '__main__':
    main()
