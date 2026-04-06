"""
DocumentLoader — 负责将 inbox/ 中的源文件加载为纯文本。
"""

from pathlib import Path

SUPPORTED_EXTENSIONS = {".md", ".txt"}


class DocumentLoader:
    def load_text(self, filepath: Path) -> str:
        """
        读取 .md 或 .txt 文件，返回纯文本内容。

        Args:
            filepath: 源文件的绝对路径

        Returns:
            文件的文本内容（UTF-8）

        Raises:
            ValueError: 文件格式不受支持
            FileNotFoundError: 文件不存在
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")

        if filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"不支持的文件格式: {filepath.suffix}，"
                f"支持的格式: {', '.join(SUPPORTED_EXTENSIONS)}"
            )

        return filepath.read_text(encoding="utf-8")
