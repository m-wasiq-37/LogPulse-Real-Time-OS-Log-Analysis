FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend/ /app/

EXPOSE 5000

CMD ["python", "app.py"]
