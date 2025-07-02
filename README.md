![mimir-cardicop logo](assets/logo-new.png)

# 🚀 Overview

mimir-cardicop is an open-source Prometheus exporter that helps you find unused, high-cardinality metrics in your Grafana Mimir deployment.

It mimics Grafana Cloud’s cardinality management dashboards, letting you:

* Enumerate all tenants in Mimir

* Fetch active metrics

* Analyze usage in recording/alerting rules

* Check if metrics are being queried (via Loki)

* Expose a Prometheus metric to mark each as used or unused

## ⚙️ Setup

You can deploy mimir-cardicop in Kubernetes using the included Helm chart.

### Prerequisites

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

Runs queries against Loki logs to see if a metric was recently used (within a configurable lookback).

✅ 5. Exporter Metrics

Publishes `/metrics` endpoint with:

```
metric_usage_status{tenant_id, metric_name} 1|0
```


## 📜 Dashboards

This repository includes Grafana dashboard JSON files under the dashboards/ folder. These dashboards visualize cardinality analysis results for Grafana Mimir tenants.

#### ⚠️ 1️⃣ Install the JSON API Datasource Plugin

To connect Grafana to the Mimir cardinality API, you must install the Grafana JSON Datasource plugin.

This plugin enables Grafana to query the cardinality HTTP API in Mimir and render the results in dashboards.

Install via Grafana CLI:

```
grafana-cli plugins install marcusolsson-json-datasource
```

Or install it from the Grafana UI Plugin catalog.

✅ Make sure the plugin is enabled in your Grafana instance before importing the dashboards.

#### ⚠️ 2️⃣ Create the Cardinality API Datasource

Once the plugin is installed, you must create a new Grafana data source of type JSON API.

Name: Mimir Cardinality API (or any meaningful name you choose)

Type: JSON API

URL:
```
<MIMIR-QUERY-FRONTEND-URL>/prometheus/api/v1/cardinality
```

Auth/Headers: Configure if needed (e.g., tokens, basic auth, etc.)

This datasource will be used specifically to query the Mimir cardinality API.

#### ⚠️ 3️⃣ Use in Conjunction with Prometheus Datasource

These dashboards require both:

  * The Prometheus datasource (for metrics)

  * The JSON API datasource (for cardinality API)

✅ When importing the dashboard, select Prometheus for the metrics panels and your Mimir Cardinality API JSON datasource for the cardinality panels.

This ensures:

  * Regular metrics come from your Prometheus instance.

  * Cardinality analysis panels call Mimir’s cardinality API endpoint directly.

#### ⚠️ 4️⃣ Important: Update the tenant variable!

Mimir does not provide a built-in metric listing all tenants. The only way to retrieve the tenant list is to query the Store Gateway API:
```
GET /store-gateway/tenants
```

✅ You should run this API to get the list of tenants your cluster has.

✅ Then update the tenant variable in each dashboard JSON file with the comma-separated list of tenant IDs.

Example:

```
"options": [
  "tenant1,tenant2,tenant3"
]
```

This ensures that dashboards correctly show data for all relevant tenants.

### How to get the tenant list

You can run:
```
curl <STORE_GATEWAY_URL>/store-gateway/tenants
```

Then, parse the output to produce the comma-separated string for the dashboard variable.

### Why is this needed?

Grafana Mimir currently has no metric to list all tenants automatically. Using the Store Gateway endpoint is the recommended approach.

### 🎯 How to use:

✅ Go to Grafana → Dashboards → Import

✅ Upload the JSON file.

✅ Set your Prometheus and JSON API data sources.

You can customize it further to match your setup.

## 📜 Recording Rules

To detect if a metric is being queried in logs (via Loki), deploy a recording rule in Mimir.

Example rule is in:

```
recording_rules/
  metric-query-recording-rule.yaml
```

### 🎯 How to apply:

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



