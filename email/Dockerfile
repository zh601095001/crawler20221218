# syntax=docker/dockerfile:1
FROM node:16.17.1-alpine3.15
RUN apk add --no-cache python3 g++ make
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install
COPY . .
# 设定时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone