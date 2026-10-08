# -*- coding: utf-8 -*-
"""临时脚本:提取项目内接口文档 PDF 的文本内容,方便阅读"""
import sys
from pypdf import PdfReader

PDF = r"e:\00_learning\PYproject01\pythonproject\电子商务项目&物流项目实战接口文档.pdf"

def main():
    reader = PdfReader(PDF)
    print(f"==== 共 {len(reader.pages)} 页 ====\n")
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        print(f"\n========== 第 {i} 页 ==========")
        print(text)

if __name__ == "__main__":
    main()
