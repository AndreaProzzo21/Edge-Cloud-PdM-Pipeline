# application/core_manager.py
import logging

class CoreManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)

    def process_message(self, raw_payload):
        try:
            # Qui potresti aggiungere logica: es. se prediction == "BROKEN", 
            # invia subito un segnale prioritario
            self.data_manager.save_prediction(raw_payload)
            self.logger.info(f"Processed data for {raw_payload.get('device_id')}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")