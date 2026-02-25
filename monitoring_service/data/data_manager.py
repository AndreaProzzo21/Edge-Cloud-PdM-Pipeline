# data/data_manager.py
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import WriteOptions

class DataManager:
    def __init__(self, url, token, org, bucket):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.bucket = bucket
        # WriteOptions(batch_size=1) per monitoring real-time, 
        # o più alto per performance
        self.write_api = self.client.write_api(write_options=WriteOptions(batch_size=1))

    def save_prediction(self, data: dict):
        point = Point("pump_predictions") \
            .tag("device_id", data["device_id"]) \
            .field("health_score", float(data["health_percent"])) \
            .field("prediction", data["prediction"]) \
            .field("vibration_rms", float(data["vibration_rms"]))
        
        self.write_api.write(bucket=self.bucket, record=point)

    def close(self):
        self.client.close()