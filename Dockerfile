# 使用官方的 Linux 初始镜像
FROM ubuntu:latest

# 安装必要的工具和依赖
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV LLM_ENDPOINT=127.0.0.1:8080
ENV APP_PORT=8561

# 克隆 Git 仓库
RUN git clone https://github.com/maxchiron/simple_chatbot

# 进入仓库目录
WORKDIR /simple_chatbot

# 安装 Python 依赖
RUN pip3 install -r requirements.txt

# 暴露 Streamlit 应用的端口
EXPOSE $APP_PORT

# 设置 Streamlit 运行命令
CMD ["streamlit", "run", "app.py", "--server.port", "$APP_PORT"]