FROM python:3-alpine3.16
WORKDIR /app
RUN apk add --no-cache python3 g++ make gcc libffi-dev zlib-dev libcec-dev libtool
RUN apk add wget && wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

