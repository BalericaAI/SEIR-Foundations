FROM --platform=linux/amd64 debian:bookworm-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends gnucobol && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY cobol/financial.cbl .
RUN cobc -x -free -o financial financial.cbl

FROM --platform=linux/amd64 debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 libcob4 ca-certificates && rm -rf /var/lib/apt/lists/* && useradd --system --uid 10001 lab
WORKDIR /opt/app
COPY --from=build /src/financial /opt/app/financial
COPY app/server.py /opt/app/server.py
USER 10001
ENV PORT=8080 PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python3", "/opt/app/server.py"]
