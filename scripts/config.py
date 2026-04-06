import os
from pathlib import Path

from dotenv import load_dotenv

# 优先加载项目根目录的 .env（本地开发）；容器内由 docker-compose env_file 注入
load_dotenv(Path(__file__).parent.parent / ".env")

LLM_BASE_URL = os.environ["LLM_BASE_URL"]
LLM_API_KEY = os.environ["LLM_API_KEY"]
LLM_MODEL_NAME = os.environ["LLM_MODEL_NAME"]
