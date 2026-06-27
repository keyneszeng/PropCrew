FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（chromadb 需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# chromadb（可选，没有会自动降级为内存模式）
RUN pip install --no-cache-dir chromadb 2>/dev/null || true

# 复制项目代码
COPY . .

# 创建数据目录
RUN mkdir -p data

# HF Spaces 默认端口
ENV PORT=7860

# 启动 Streamlit（web/app.py 为入口）
CMD streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false
