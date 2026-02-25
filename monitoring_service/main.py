import os
import time
import logging
from communication.mqtt.mqtt_fetcher import MQTTFetcher
from application.core_manager import CoreManager
from data.data_manager import DataManager

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MonitoringService")

def main():
    logger.info("Starting Monitoring Service...")

    # 1. Caricamento Config (Environment Variables)
    mqtt_broker = os.getenv("MONITOR_MQTT_BROKER")
    mqtt_port = int(os.getenv("MONITOR_MQTT_PORT", 1883))
    mqtt_topic = os.getenv("MONITOR_TOPIC")

    influx_url = os.getenv("INFLUX_URL", "http://influxdb:8086")
    influx_token = os.getenv("INFLUX_TOKEN", "token-segreto")
    influx_org = os.getenv("INFLUX_ORG", "pdm_org")
    influx_bucket = os.getenv("INFLUX_BUCKET", "monitoring_bucket")

    # 2. Inizializzazione Layer (Bottom-Up)
    try:
        data_manager = DataManager(influx_url, influx_token, influx_org, influx_bucket)
        core_manager = CoreManager(data_manager)
        fetcher = MQTTFetcher(mqtt_broker, mqtt_port, mqtt_topic, core_manager)

        # 3. Start Fetcher
        logger.info(f"Connecting to MQTT Broker: {mqtt_broker}:{mqtt_port}")
        fetcher.start()

        # Keep-alive loop
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        logger.info("Service stopping...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        data_manager.close()

if __name__ == "__main__":
    main()