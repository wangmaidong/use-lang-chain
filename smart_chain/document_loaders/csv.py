import os
from ..documents import Document
import csv


# 定义 CSVLoader 类
class CSVLoader:
    """
    CSV 加载器：读取 CSV 文件，将每一行转换为 Document 对象。
    每行数据格式化为 "列名: 值\n列名: 值..." 的文本格式。
    """

    # 构造函数，初始化类成员变量
    def __init__(
        self,
        file_path,  # CSV 文件路径
        source_column=None,  # 指定 source 的列名（可选）
        metadata_columns=(),  # 指定作为元数据的列列表（可选）
        csv_args=None,  # 传递给 csv.DictReader 的参数（可选）
        encoding=None,  # 文件编码（可选）
        autodetect_encoding=False,  # 是否自动检测编码（可选）
    ):
        # 保存文件路径
        self.file_path = file_path
        # 保存 source 列名称
        self.source_column = source_column
        # 保存元数据列列表
        self.metadata_columns = metadata_columns
        # 如果 csv_args 为 None，则用空字典
        self.csv_args = csv_args or {}
        # 保存文件编码
        self.encoding = encoding
        # 保存是否自动检测编码
        self.autodetect_encoding = autodetect_encoding

    # 加载 CSV 文件并返回 Document 对象列表
    def load(self):
        """
        加载 CSV 文件并返回 Document 列表。
        Returns:
            Document 对象列表，每行 CSV 对应一个 Document
        """
        # 检查指定的文件路径是否存在
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"文件不存在: {self.file_path}")
        # 初始化 Document 列表
        docs = []
        # 尝试使用指定的编码打开文件
        try:
            # 打开 CSV 文件，指定换行和编码
            with open(self.file_path, newline="", encoding=self.encoding) as csvfile:
                # 调用内部方法读取文件并生成 Document 列表
                docs = self._read_file(csvfile)
        # 捕获解码错误（编码不匹配时）
        except UnicodeDecodeError as e:
            # 如果设置了自动检测编码
            if self.autodetect_encoding:
                # 依次尝试常见的几种编码
                encodings_to_try = ["utf-8", "utf-8-sig", "gbk", "latin-1"]
                for enc in encodings_to_try:
                    try:
                        # 按当前尝试的编码重新打开文件
                        with open(self.file_path, newline="", encoding=enc) as csvfile:
                            # 读取文件
                            docs = self._read_file(csvfile)
                            # 如果读取成功则结束尝试
                            break
                    except UnicodeDecodeError:
                        # 解码失败则继续尝试下一个编码
                        continue
                # 如果所有编码都读取失败，抛出异常
                if not docs:
                    raise RuntimeError(
                        f"无法以常见编码读取文件 {self.file_path}"
                    ) from e
            else:
                # 未设置自动检测编码，直接抛出运行时异常
                raise RuntimeError(f"编码错误，无法读取文件 {self.file_path}") from e
        # 捕获其他打开或读取文件的异常
        except Exception as e:
            # 抛出运行时异常，包含原始异常信息
            raise RuntimeError(f"读取文件 {self.file_path} 时出错") from e
        # 返回 Document 列表
        return docs

    # 内部方法：读取 CSV 文件内容并生成每行的 Document
    def _read_file(self, csvfile):
        """
        从已打开的 CSV 文件中读取数据并生成 Document 对象。
        Args:
            csvfile: 已打开的 CSV 文件对象
        Returns:
            Document 对象列表
        """
        # 初始化 Document 列表
        docs = []
        # 使用 DictReader 处理 csv，每行是一个字典
        csv_reader = csv.DictReader(csvfile, **self.csv_args)
        # 遍历每一行数据
        for i, row in enumerate(csv_reader):
            # 确定 source 元数据
            try:
                # 如果指定了 source 列名，则取该列的值
                if self.source_column is not None:
                    source = row[self.source_column]
                else:
                    # 未指定时以文件路径为 source
                    source = str(self.file_path)
            except KeyError:
                # 指定的 source 列名不存在时报错
                raise ValueError(f"源列 '{self.source_column}' 在 CSV 文件中不存在。")
            # 构造文档主体内容（排除元数据列）
            content_parts = []
            # 遍历每列字段及其值
            for k, v in row.items():
                # 跳过元数据列，只加入正文内容
                if k not in self.metadata_columns:
                    # 去除列名两端空白
                    key = k.strip() if k is not None else ""
                    # 若值为字符串则去两端空白，否则转为字符串
                    if isinstance(v, str):
                        value = v.strip()
                    else:
                        value = str(v) if v is not None else ""
                    # 拼接为 '列名: 值' 形式加入内容列表
                    content_parts.append(f"{key}: {value}")
            # 用换行连接所有列内容，组成正文内容
            content = "\n".join(content_parts)
            # 构建元数据字典，包括 source 和行号
            metadata = {
                "source": source,
                "row": i,  # 行号，从0开始
            }
            # 添加额外指定的元数据列
            for col in self.metadata_columns:
                try:
                    # 取出元数据列的值
                    metadata[col] = row[col]
                except KeyError:
                    # 元数据列不存在时报错
                    raise ValueError(f"元数据列 '{col}' 在 CSV 文件中不存在。")
            # 创建 Document 对象并添加到文档列表
            docs.append(Document(page_content=content, metadata=metadata))
        # 返回所有生成的 Document 对象列表
        return docs
