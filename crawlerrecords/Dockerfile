FROM node:16.17.1-alpine3.15
WORKDIR /app
RUN apk add --no-cache python3 g++ make gcc
RUN apk add wget && wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# 设定时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
