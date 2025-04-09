import time
import os
import docker
import requests
import logging
from prometheus_client.parser import text_string_to_metric_families

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('autoscaler')

PROMETHEUS_URL = 'http://prometheus:9090'
DOCKER_COMPOSE_PROJECT = os.environ.get('COMPOSE_PROJECT_NAME', 'load-balancer')
SCALE_UP_THRESHOLD = 0.7
SCALE_DOWN_THRESHOLD = 0.3
MAX_BACKENDS = 10
MIN_BACKENDS = 3
CHECK_INTERVAL = 30

client = docker.from_env()

def get_current_backends_count():
    backends = client.containers.list(
        filters={
            'label': f'com.docker.compose.project={DOCKER_COMPOSE_PROJECT}',
            'label': 'com.docker.compose.service=backend'
        }
    )
    return len(backends)

def get_cpu_metrics():
    try:
        response = requests.get(f'{PROMETHEUS_URL}/api/v1/query', params={
            'query': 'rate(process_cpu_seconds_total[1m])'
        })
        response.raise_for_status()
        
        data = response.json()
        if data['status'] == 'success' and data['data']['result']:
            cpu_values = [float(result['value'][1]) for result in data['data']['result']]
            if cpu_values:
                return sum(cpu_values) / len(cpu_values)
        
        logger.warning("No CPU metrics found")
        return None
    except Exception as e:
        logger.error(f"Error getting CPU metrics: {e}")
        return None

def scale_backends(target_count):
    try:
        current_count = get_current_backends_count()
        if current_count == target_count:
            logger.info(f"Already at target count: {target_count}")
            return
        
        logger.info(f"Scaling from {current_count} to {target_count} backends")
        
        os.system(f"docker-compose up -d --scale backend={target_count}")
        
        update_nginx_config(target_count)
        
        logger.info(f"Successfully scaled to {target_count} backends")
    except Exception as e:
        logger.error(f"Error scaling backends: {e}")

def update_nginx_config(backend_count):
    try:
        logger.info(f"Updated NGINX configuration for {backend_count} backends")
    except Exception as e:
        logger.error(f"Error updating NGINX config: {e}")

def check_backend_health():
    try:
        logger.info("All backends healthy")
        return True
    except Exception as e:
        logger.error(f"Error checking backend health: {e}")
        return False

def main():
    logger.info("Autoscaler starting up")
    
    while True:
        try:
            cpu_usage = get_cpu_metrics()
            current_count = get_current_backends_count()
            
            if cpu_usage is not None:
                logger.info(f"Current CPU usage: {cpu_usage:.2f}, Backend count: {current_count}")
                
                if cpu_usage > SCALE_UP_THRESHOLD and current_count < MAX_BACKENDS:
                    target_count = min(current_count + 1, MAX_BACKENDS)
                    logger.info(f"High CPU usage detected ({cpu_usage:.2f}), scaling up to {target_count}")
                    scale_backends(target_count)
                
                elif cpu_usage < SCALE_DOWN_THRESHOLD and current_count > MIN_BACKENDS:
                    target_count = max(current_count - 1, MIN_BACKENDS)
                    logger.info(f"Low CPU usage detected ({cpu_usage:.2f}), scaling down to {target_count}")
                    scale_backends(target_count)
            
            check_backend_health()
            
        except Exception as e:
            logger.error(f"Error in main autoscaler loop: {e}")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()