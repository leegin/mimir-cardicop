FROM --platform=linux/amd64 python:3.11.7 AS build

# Install curl for mimirtool download
RUN apt-get update && apt-get install -y curl

# Install mimirtool
RUN curl -L -o /usr/local/bin/mimirtool https://github.com/grafana/mimir/releases/latest/download/mimirtool-linux-amd64 \
    && chmod +x /usr/local/bin/mimirtool

# Verify mimirtool
RUN mimirtool version

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy code
COPY exporter/ exporter/
COPY main.py .

# Set PYTHONPATH so imports work
ENV PYTHONPATH=/app

# Run the exporter
CMD ["python3", "main.py"]
