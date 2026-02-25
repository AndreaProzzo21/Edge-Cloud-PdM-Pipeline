import os
import pandas as pd
import json
from datetime import datetime
import logging

logger = logging.getLogger("InferenceManager")

class InferenceManager:
    def __init__(self, predictor, base_output_path, mqtt_client=None):
       
        self.predictor = predictor
        self.base_output_path = base_output_path
        self.mqtt_client = mqtt_client
        
        # Creiamo la cartella di output se non esiste
        if not os.path.exists(self.base_output_path):
            os.makedirs(self.base_output_path)
            logger.info(f"📂 Cartella creata: {self.base_output_path}")

    def process_data(self, data):
        # 1. Recupero ID dispositivo
        pump_id = data.get('device_id', 'unknown_device')
        
        # 2. Esecuzione Inferenza
        predicted_state = self.predictor.predict(data)
        
        # 3. Arricchimento Payload
        data['predicted_state'] = predicted_state
        data['inference_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"🔮 [{pump_id}] Predizione: {predicted_state}")

        # 4. Salvataggio su file specifico per pompa
        self._save_to_device_csv(pump_id, data)

        # 5. Pubblicazione MQTT (Topic dinamico per lo scaling)
        if self.mqtt_client:
            output_topic = f"factory/pumps/{pump_id}/predictions"
            self.mqtt_client.publish(output_topic, json.dumps(data))

    def _save_to_device_csv(self, pump_id, data):
        # Generiamo il path: es. /app/data/output/PUMP-001.csv
        file_path = os.path.join(self.base_output_path, f"{pump_id}.csv")
        
        df = pd.DataFrame([data])
        file_exists = os.path.isfile(file_path)
        
        # Scriviamo in append sul file specifico
        df.to_csv(file_path, mode='a', index=False, header=not file_exists)