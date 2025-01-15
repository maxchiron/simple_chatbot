# Simple Chatbot / 简单聊天机器人

## Description / 描述

This project is a simple chatbot implemented using Python and Streamlit. It can be deployed locally or using Docker for easy scalability.

这个项目是一个使用Python和Streamlit实现的简单聊天机器人。它可以在本地部署，也可以使用Docker部署以便于扩展。

## Features / 功能

- Simple and intuitive user interface / 简单直观的用户界面
- Real-time chat interaction / 实时聊天交互
- Basic natural language processing capabilities / 基本的自然语言处理能力
- Customizable responses based on user input / 根据用户输入自定义响应
- Easy integration with other Python libraries for extended functionality / 易于与其他Python库集成以扩展功能

## Local Deployment / 本地部署

### Setup / 设置

1. Clone the repository / 克隆仓库
   ```
   git clone <repository-url>
   cd simple_chatbot
   ```

2. Install dependencies / 安装依赖
   ```
   pip install -r requirements.txt
   ```

### Usage / 使用方法

1. Run the Streamlit app locally / 在本地运行Streamlit应用
   ```
   streamlit run streamlit_app.py
   ```

2. Open your web browser and navigate to `http://localhost:8501` / 打开网页浏览器并访问 `http://localhost:8501`

## Docker Deployment / Docker部署

### Setup / 设置

1. Clone the repository / 克隆仓库
   ```
   git clone <repository-url>
   cd simple_chatbot
   ```

2. Build Docker image / 构建Docker镜像
   ```
   docker build -t simple_chatbot .
   ```

### Usage / 使用方法

1. Run the Docker container / 运行Docker容器
   ```
   docker run -p 8501:8501 simple_chatbot
   ```

2. Open your web browser and navigate to `http://localhost:8501` / 打开网页浏览器并访问 `http://localhost:8501`

## File Structure / 文件结构

- `.gitignore`: Specifies intentionally untracked files to ignore / 指定要忽略的未跟踪文件
- `Dockerfile`: Contains instructions for building the Docker image / 包含构建Docker镜像的指令
- `requirements.txt`: Lists the Python dependencies for the project / 列出项目的Python依赖项
- `streamlit_app.py`: The main application file containing the Streamlit app and chatbot logic / 包含Streamlit应用和聊天机器人逻辑的主应用文件

## Contributing / 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献！请随时提交 Pull Request。

## License / 许可证

This project is open source and available under the [MIT License](LICENSE).

该项目是开源的，适用于 [MIT 许可证](LICENSE)。
