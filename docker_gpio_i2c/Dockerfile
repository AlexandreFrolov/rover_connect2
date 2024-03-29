FROM alpine:latest
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN apk update && \
  apk add --no-cache \
  g++ gcc python3 py3-pip python3-dev git musl-dev libffi-dev openssl-dev sudo && \
  rm -rf /var/cache/apk/*  
COPY . /app  
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python3", "bme380.py"]

