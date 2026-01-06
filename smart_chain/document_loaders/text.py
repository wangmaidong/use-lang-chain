import os
from ..documents import Document


class TextLoader:
    def __init__(self, file_path, encoding=None, autodetect_encoding=False):
        self.file_path = file_path
        self.encoding = encoding
        self.autodetect_encoding = autodetect_encoding

    def load(self):
        content = self._detect_and_read()
        metadata = {"source": self.file_path}
        return [Document(page_content=content, metadata=metadata)]

    def _detect_and_read(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"文件不存在:{self.file_path}")
        if self.encoding:
            with open(
                self.file_path, "r", encoding=self.encoding, errors="ignore"
            ) as file:
                return file.read()
        tried = []
        for encoding in (
            ["utf-8", "gbk", "latin-1"] if self.autodetect_encoding else ["utf-8"]
        ):
            try:
                with open(self.file_path, "r", encoding=encoding) as file:
                    return file.read()
            except Exception as e:
                tried.append((encoding, str(e)))
                continue
        raise UnicodeDecodeError(
            "auto", b"", 0, 1, f"无法以常见的编码读取文件,尝试过{tried}"
        )
