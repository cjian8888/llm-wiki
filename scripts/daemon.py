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

INBOX_DIR = Path(__file__).parent.parent / "inbox"
WATCHED_EXTENSIONS = {".md", ".txt"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("wiki-daemon")


class InboxHandler(FileSystemEventHandler):
    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() not in WATCHED_EXTENSIONS:
            return
        logger.info(f"[Daemon] 检测到新文件: {path.name}，准备触发摄入管道...")
        # TODO: 调用 ingest pipeline
        # from scripts.ingest import run_ingest
        # run_ingest(path)


def main() -> None:
    if not INBOX_DIR.exists():
        logger.error(f"inbox 目录不存在: {INBOX_DIR}")
        sys.exit(1)

    logger.info(f"[Daemon] 启动，监听目录: {INBOX_DIR}")

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
