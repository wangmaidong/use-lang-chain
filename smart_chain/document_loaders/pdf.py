import os
from ..documents import Document
import PyPDF2


class PyPDFLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        docs = []
        with open(self.file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for idx, page in enumerate(reader.pages):
                content = page.extract_text() or ""
                metadata = {
                    "source": self.file_path,
                    "page": idx + 1,
                    "total_pages": len(reader.pages),
                }
                docs.append(Document(page_content=content, metadata=metadata))
        return docs
