FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app

# 翻译模型目录（ENABLE_TRANSLATION=true 时会自动下载到此目录）
ENV ARGOS_PACKAGES_DIR=/app/models/argos-translate/packages
ENV ENABLE_TRANSLATION=false

RUN apt-get update && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

COPY . .

# 入口脚本：按需下载翻译模型，再转交 tini 执行 streamlit
COPY scripts/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8501

VOLUME ["/app/chroma_db", "/app/docs", "/app/models/argos-translate/packages"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501')" || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=none"]
