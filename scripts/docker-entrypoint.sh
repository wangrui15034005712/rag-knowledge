#!/bin/bash
set -e

# 翻译模型按需下载（默认不下载，可加速启动）
if [ "${ENABLE_TRANSLATION}" = "true" ]; then
    echo "[entrypoint] ENABLE_TRANSLATION=true, downloading translation models..."
    python scripts/download_argos_model.py
    echo "[entrypoint] Translation models ready."
else
    echo "[entrypoint] ENABLE_TRANSLATION=false, skipping translation model download."
fi

# 转交给 tini 执行 CMD（streamlit）
exec tini -- "$@"
