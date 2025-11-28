# 使用轻量级的 Python 基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到容器中
COPY . .

# 创建数据目录（如果不存在），用于挂载卷
RUN mkdir -p saves presets

# 暴露端口 (与 config.json 中的默认端口保持一致)
EXPOSE 169

# 声明数据卷，以便持久化保存数据
VOLUME ["/app/saves", "/app/presets", "/app/config.json"]

# 启动服务器
# -u 参数表示使用无缓冲输出，方便查看日志
CMD ["python", "-u", "server.py"]