FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir paho-mqtt smbus2

COPY i2c-bridge.py /app/i2c-bridge.py

CMD ["python", "i2c-bridge.py"]
