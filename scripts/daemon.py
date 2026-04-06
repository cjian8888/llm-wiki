"""
LLM Wiki 守护进程
持续监听 inbox/ 目录，检测到新文件时触发摄入管道。
"""

import logging
import sys
import time
from pathlib import Path

from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer

sys.path.insert(0, str(Path(__file__).parent))
from ingest import run_ingest

INBOX_DIR = Path(__file__).parent.parent / "inbox"
WATCHED_EXTENSIONS = {".md", ".txt"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("wiki-daemon")


def _should_ingest(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in WATCHED_EXTENSIONS


def _ingest_file(path: Path, source: str) -> None:
    logger.info(f"[Daemon] {source}: {path.name}，触发摄入管道...")
    try:
        run_ingest(path)
    except Exception as e:
        logger.error(f"[Daemon] 摄入失败: {path.name} — {e}", exc_info=True)


class InboxHandler(FileSystemEventHandler):
    def on_created(self, event: FileCreatedEvent) -> None:
        path = Path(event.src_path)
        if not _should_ingest(path):
            return
        _ingest_file(path, "检测到新文件")


def main() -> None:
    if not INBOX_DIR.exists():
        logger.error(f"inbox 目录不存在: {INBOX_DIR}")
        sys.exit(1)

    logger.info(f"[Daemon] 启动，监听目录: {INBOX_DIR}")

    for path in sorted(INBOX_DIR.iterdir()):
        if _should_ingest(path):
            _ingest_file(path, "发现积压文件")

    observer = Observer()
    observer.schedule(InboxHandler(), str(INBOX_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("[Daemon] 收到停止信号，退出。")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
