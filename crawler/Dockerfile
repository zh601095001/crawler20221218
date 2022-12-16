FROM node:16.17.1-ubuntu:20.06
WORKDIR /app
RUN apk add --no-cache python3 g++ make gcc libffi-dev zlib-dev libcec-dev libtool
RUN apk add wget && wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY package.json yarn.lock ./
RUN yarn install
COPY . .
COPY chromedriver /usr/bin
RUN chmod 111 /usr/bin/chromedriver
COPY  google-chrome-stable_current_i386.deb .
RUN sudo dpkg -i google-chrome-stable_current_i386.deb

