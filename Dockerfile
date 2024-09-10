# 使用官方 Python 镜像作为基础镜像
FROM python:3.10.14-slim AS builder

# 设置工作目录
WORKDIR /app

# # 创建 sources.list 文件并设置使用清华大学的镜像源
# RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main contrib non-free" > /etc/apt/sources.list && \
#     echo "deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main contrib non-free" >> /etc/apt/sources.list && \
#     echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
#     echo "deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
#     echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-backports main contrib non-free" >> /etc/apt/sources.list && \
#     echo "deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-backports main contrib non-free" >> /etc/apt/sources.list && \
#     echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list && \
#     echo "deb-src https://mirrors.tuna.tsinghua.edu.cn/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list

# 创建 /etc/apt/sources.list 文件并添加阿里云的源
RUN echo "deb https://mirrors.aliyun.com/debian/ bullseye main contrib non-free" > /etc/apt/sources.list && \
    echo "deb-src https://mirrors.aliyun.com/debian/ bullseye main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.aliyun.com/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bullseye-backports main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.aliyun.com/debian/ bullseye-backports main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.aliyun.com/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list


# 安装构建工具和其他依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    curl \
    portaudio19-dev \
    ffmpeg \
    iputils-ping \
    telnet


# 使用阿里云镜像
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/  && \
    pip config set install.trusted-host mirrors.aliyun.com
# # 复制 pyproject.toml 和 poetry.lock（如果存在）
# COPY pyproject.toml poetry.lock* ./

# 安装依赖
RUN pip install --no-cache-dir --upgrade  poetry

# build project

FROM python:3.10.14-slim 
# 从builder镜像复制环境
COPY --from=builder /usr/local /usr/local
COPY --from=builder /usr/lib /usr/lib
COPY --from=builder /usr/include /usr/include
COPY --from=builder /bin /bin
COPY --from=builder /lib /lib
COPY --from=builder /lib64 /lib64


# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . .
RUN poetry config virtualenvs.create false
RUN poetry install

# 暴露  默认端口
EXPOSE 8000

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ARG COMMIT_SHA
ENV COMMIT_SHA ${COMMIT_SHA}

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]