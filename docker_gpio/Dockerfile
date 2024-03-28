FROM alpine:latest
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN apk update && \
  apk add --no-cache \
  g++ gcc python3 py3-pip python3-dev git musl-dev libffi-dev openssl-dev sudo && \
  rm -rf /var/cache/apk/*  && \
  git clone https://gitflic.ru/project/repka_pi/repkapigpiofs.git && \
  cd repkapigpiofs && \
  python3 setup.py install

WORKDIR /app/repkapigpiofs/Demo
CMD ["python3", "blink_led.py"]

