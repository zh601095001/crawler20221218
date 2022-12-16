# syntax=docker/dockerfile:1
FROM node:16.17.1-alpine3.15
RUN apk add --no-cache python3 g++ make
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install
COPY . .
