FROM debian:bookworm-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends gnucobol gcc libc6-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY hello.cbl .
RUN cobc -x -free -o /seir-finance hello.cbl

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends libcob4 && rm -rf /var/lib/apt/lists/* && useradd -r -u 10001 coboluser
COPY --from=build /seir-finance /usr/local/bin/seir-finance
USER coboluser
ENTRYPOINT ["/usr/local/bin/seir-finance"]
