# Network Load Balancer Project

This project implements a complete network load balancer system using NGINX with automatic scaling, health checks, and monitoring capabilities.

## Features

- NGINX-based load balancing with weighted distribution and failover
- Automatic scaling based on CPU usage metrics
- Health monitoring for backend services
- Prometheus metrics collection
- Grafana dashboards for visualization
- Load testing capabilities

## Prerequisites

- Docker and Docker Compose
- Python 3.7+ (for load testing)
- matplotlib (for load test visualization)

## Project Structure

```
network-load-balancer/
│
├── nginx.conf                 # NGINX load balancer configuration
├── docker-compose.yml         # Main Docker Compose configuration
├── prometheus.yml             # Prometheus monitoring configuration
├── load_test.py               # Load testing script
│
├── backend/                   # Backend service directory
│   ├── app.py                 # Flask application for backend service
│   ├── Dockerfile             # Dockerfile for backend service
│   └── requirements.txt       # Python dependencies for backend
│
└── autoscaler/                # Autoscaler service directory
    ├── autoscaler.py          # Autoscaling script
    ├── Dockerfile             # Dockerfile for autoscaler
    └── requirements.txt       # Python dependencies for autoscaler
```

## Setup Instructions

1. Clone this repository:
```bash
git clone <repository-url>
cd network-load-balancer
```

2. Create a directory for NGINX logs:
```bash
mkdir nginx_logs
```

3. Build and start the services:
```bash
docker-compose up -d
```

4. Verify all services are running:
```bash
docker-compose ps
```

## Accessing Services

- **Load Balancer**: http://localhost:80
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
  - Default login: admin/admin
  - Add Prometheus as a data source with URL: http://prometheus:9090
  - Import the dashboard from the grafana-dashboard.json file

## Running a Load Test

To test the load balancer with simulated traffic:

```bash
python load_test.py --duration 60 --threads 20 --rps 50
```

Parameters:
- `--duration`: Test duration in seconds (default: 60)
- `--threads`: Number of concurrent threads (default: 10)
- `--rps`: Requests per second (default: 10)
- `--url`: Target URL (default: http://localhost:80)

The test will generate a graph of response times and server distribution saved as `load_test_results.png`.

## Testing Autoscaling

To test the autoscaling capability, generate high load:

```bash
curl "http://localhost/load?intensity=10&duration=5"
```

Monitor the autoscaler logs to see scaling events:

```bash
docker-compose logs -f autoscaler
```

## Configuration

### NGINX Load Balancer

The NGINX configuration uses the least connections balancing algorithm with weighted backend servers. Modify the weights in `nginx.conf` to adjust traffic distribution.

### Autoscaler

The autoscaler monitors CPU usage and scales backend services based on the following thresholds:

- Scale up when CPU exceeds 70% (`SCALE_UP_THRESHOLD` in autoscaler.py)
- Scale down when CPU is below 30% (`SCALE_DOWN_THRESHOLD` in autoscaler.py)
- Minimum backends: 3 (`MIN_BACKENDS`)
- Maximum backends: 10 (`MAX_BACKENDS`)

## Troubleshooting

- If services don't start properly, check logs with:
  ```bash
  docker-compose logs [service_name]
  ```

- If the autoscaler doesn't work, ensure Docker socket is mounted properly and the autoscaler has permissions to use it.

- If Grafana dashboards don't show data, make sure Prometheus is correctly configured and collecting metrics.

## License

MIT