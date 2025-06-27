## 🚀 Overview

mimir-cardicop is an open-source Prometheus exporter that helps you find unused, high-cardinality metrics in your Grafana Mimir deployment.

It mimics Grafana Cloud’s cardinality management dashboards, letting you:

* Enumerate all tenants in Mimir

* Fetch active metrics

* Analyze usage in recording/alerting rules

* Check if metrics are being queried (via Loki)

* Expose a Prometheus metric to mark each as used or unused

## ⚙️ Setup

You can deploy mimir-cardicop in Kubernetes using the included Helm chart.

## Prerequisites

* Grafana Mimir (with Store Gateway, Ruler, and Query Frontend)

* Grafana Loki (for query analysis)

* Kubernetes cluster

* Helm 3.x

1️⃣ Clone the repository
```
git clone https://github.com/your-org/mimir-cardicop.git
cd mimir-cardicop
```

2️⃣ Build and Push the Container (optional)
```
docker build -t ghcr.io/your-org/mimir-cardicop:latest .
docker push ghcr.io/your-org/mimir-cardicop:latest
```
3️⃣ Deploy with Helm
Edit your charts/mimir-cardicop/values.yaml:

```
env:
  GRAFANA_URL: "http://grafana.yourdomain.com"
  GRAFANA_ADMIN_USER: "admin"
  GRAFANA_ADMIN_PASSWORD: "yourpassword"
  STORE_GATEWAY_URL: "http://mimir-store-gateway.namespace:8080/store-gateway/tenants"
  MIMIR_CARDINALITY_URL: "https://mimir-query-frontend/api/v1/cardinality/label_values"
  MIMIR_QUERY_URL: "https://mimir-query-frontend/api/v1/query_range"
  MIMIR_RULER_URL: "http://mimir-ruler.namespace:8080"
  LOKI_QUERY_TENANT_ID: "your-loki-tenant"
  LOKI_QUERY_METRIC_NAME: "metric:query:count15s"
  LOKI_QUERY_LOOKBACK_DAYS: 7
```

Then install:

```
helm install mimir-cardicop charts/mimir-cardicop/ -n your-namespace
```

## 🧭 How it works

✅ 1. Discover Tenants
Scrapes Mimir Store Gateway’s /tenants page to list all tenants.

✅ 2. Grafana Rule Analysis
Uses Grafana admin APIs to enumerate organizations, switches context, and runs mimirtool analyze grafana.

✅ 3. Mimir Rule & Prometheus Analysis
Runs mimirtool analyze ruler and analyze prometheus for each tenant, collecting metrics from rules.

✅ 4. Loki Query Analysis
Runs queries against Loki logs to see if a metric was recently used (within configurable lookback).

✅ 5. Exporter Metrics
Publishes /metrics endpoint with:

```
metric_usage_status{tenant_id, metric_name} 1|0
```


## 📜 Dashboards

Grafana dashboard JSON for visualizing usage is included in:

```
dashboards/
  mimir-cardicop-dashboard.json
```

## 🎯 How to use:

✅ Go to Grafana → Dashboards → Import

✅ Upload the JSON file

✅ Set your Prometheus data source

You can customize it further to match your setup.

## 📜 Recording Rules

To detect if a metric is being queried in logs (via Loki), deploy a recording rule in Mimir.

Example rule is in:

```
recording-rules/
  metric-query-recording-rule.yaml
```

It typically looks like:

```
groups:
  - name: metric-query-logs
    interval: 5m
    rules:
      - record: metric:query:count15s
        expr: |
          sum(count_over_time(
            {app="loki", job="loki"} |~ "query=~\".*\"" [15s]
          )) by (query)
```

## 🎯 How to apply:

✅ Adapt labels/selectors to match your Loki deployment.

✅ Upload this recording rule to your Mimir Ruler.

✅ Ensure it runs at regular intervals.

This rule makes the metric:query:count15s series available, which mimir-cardicop uses to check if a metric has been queried recently.

## 🤝 How to Contribute

We welcome contributions!

1️⃣ Fork the repo

2️⃣ Create a feature branch (git checkout -b feature/your-feature)

3️⃣ Make your changes

4️⃣ Commit and push (git push origin feature/your-feature)

5️⃣ Open a Pull Request

✅ Follow PEP8

✅ Add docstrings and tests if introducing new functionality



