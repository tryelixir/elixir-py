# OpenTelemetry

## Clickhouse

### Installation

1. Install Clickhouse:

```bash
docker run -d --name some-clickhouse-server -p 8123:8123 -p 9000:9000 yandex/clickhouse-server
```

2. Create Clickhouse DB / Table:

```bash
docker exec -it some-clickhouse-server clickhouse-client
```

3. Get the IP and replace the value wihin `opentelemetry/otel-config.yaml`:

```bash
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' some-clickhouse-server
```

4. To download the contents of the Clickhouse server, run the following:

```bash
docker exec -it 8202a4e8d79e clickhouse-client --query="SELECT * FROM otel_events.otel_traces" --format=CSVWithNames > traces.csv
```

## Otel Collector

1. Follow the prerequisite and installation instructions here: https://opentelemetry.io/docs/collector/quick-start/

2. Start the OTel collector:

```bash
docker build -f Dockerfile -t otel-collector-clickhouse .
docker run -p 4317:4317 -p 4318:4318 -p 55679:55679 otel-collector-clickhouse
```
