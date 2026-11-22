FROM python:3.12-slim-bookworm AS builder
RUN apt-get update && apt-get install -y --no-install-recommends gnucobol && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY cobol/finance.cbl ./finance.cbl
RUN cobc -x -free -o /build/finance /build/finance.cbl

FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends libcob4 && rm -rf /var/lib/apt/lists/* && useradd -r -u 10001 appuser
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=builder /build/finance /usr/local/bin/finance
COPY app ./app
USER appuser
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
