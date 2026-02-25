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
        
        if not os.path.exists(self.base_output_path):
            os.makedirs(self.base_output_path)

    def process_data(self, data):
        pump_id = data.get('device_id', 'unknown_device')
        
        # Esecuzione Inferenza (restituisce ora un dizionario)
        prediction = self.predictor.predict(data)
        
        if prediction:
            # SOSTITUIAMO i valori di debug con quelli predetti dall'IA
            # Manteniamo i nomi originali per non rompere i database a valle
            data['state'] = prediction['state']
            data['health_percent'] = prediction['health']
            data['is_ai_prediction'] = True # Flag utile per distinguere dai dati reali
        else:
            logger.warning(f"⚠️ Salto inferenza per {pump_id} a causa di dati incompleti.")
            return

        data['inference_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"🔮 [{pump_id}] Stato: {data['state']} | Salute Predetta: {data['health_percent']}%")

        # Salvataggio e Pubblicazione
        self._save_to_device_csv(pump_id, data)

        if self.mqtt_client:
            output_topic = f"factory/pumps/{pump_id}/predictions"
            self.mqtt_client.publish(output_topic, json.dumps(data))

    def _save_to_device_csv(self, pump_id, data):
        file_path = os.path.join(self.base_output_path, f"{pump_id}.csv")
        df = pd.DataFrame([data])
        file_exists = os.path.isfile(file_path)
        df.to_csv(file_path, mode='a', index=False, header=not file_exists)