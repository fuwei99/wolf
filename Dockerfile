# 使用轻量级 Python 镜像
FROM python:3.11-slim

# 设置环境变量，确保 Python 输出直接打印到日志中
ENV PYTHONUNBUFFERED=1

# Hugging Face Spaces 默认使用 UID 1000 运行
# 我们创建一个用户并设置工作目录权限
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

# 提前创建必要的目录并设置权限，确保应用可以写入
RUN mkdir -p saves presets logs && \
    chown -R user:user /home/user/app && \
    chmod -R 777 /home/user/app

# 切换到非 root 用户
USER user

# 复制项目文件
# 注意：.dockerignore 会自动过滤掉不需要的文件
COPY --chown=user:user . .

# 暴露 Hugging Face 要求的 7860 端口
EXPOSE 7860

# 启动服务
CMD ["python3", "server.py"]

