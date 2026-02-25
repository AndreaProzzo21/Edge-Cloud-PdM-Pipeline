import time
import json
import random
import math
import threading
import os
import paho.mqtt.client as mqtt

class PumpSimulator:
    def __init__(self, pump_id, broker, port, base_topic, mode="NOMINAL"):
        self.pump_id = pump_id
        self.broker = broker
        self.port = port
        self.topic = f"{base_topic}/{pump_id}/telemetry"
        self.mode = mode
        
        # Configurazione dinamica della "velocità" del tempo
        self._setup_mode_params()
        
        self.health_percent = 100.0
        self.cycle_count = 0
        
        # Baseline fisica
        self.baseline = {
            "temp": 38.0 + random.uniform(-2, 2),
            "current": 7.8 + random.uniform(-0.5, 0.5),
            "pressure": 4.2 + random.uniform(-0.3, 0.3),
            "rpm": 2850 + random.randint(-15, 15),
            "vib_x": 1.1, "vib_y": 0.7, "vib_z": 0.9
        }

        self.client = mqtt.Client(client_id=f"Sim-{pump_id}")

    def _setup_mode_params(self):
        """Configura la durata della vita in base alla modalità"""
        if self.mode == "STRESS":
            self.total_life_cycles = 150  # Vita brevissima
            self.interval = 1             # Invio ogni secondo (Totale: 2.5 min)
        elif self.mode == "ACCELERATED":
            self.total_life_cycles = 600  # Vita media
            self.interval = 2             # Invio ogni 2 secondi (Totale: 20 min)
        else: # NOMINAL
            self.total_life_cycles = random.randint(8000, 12000)
            self.interval = 10            # Invio ogni 10 secondi (Totale: ~27 ore)

    def update_degradation(self):
        self.cycle_count += 1
        life_consumed = min(self.cycle_count / self.total_life_cycles, 1.0)
        
        # Curva esponenziale per rendere il finale più drammatico
        # HEALTHY -> WARNING (intorno al 60%) -> FAULTY (intorno all'85%)
        factor = pow(life_consumed, 2.5)
        self.health_percent = max(0.0, 100.0 * (1.0 - factor))

    def generate_data(self):
        # Il fattore di usura (0.0 a 1.0)
        wear_f = (100.0 - self.health_percent) / 100.0
        wear_vib = pow(wear_f, 2.0) * 10.0 

        # Calcolo sensori influenzato dall'usura
        v_x = self.baseline["vib_x"] + random.uniform(-0.1, 0.1) + (wear_vib * 1.2)
        v_y = self.baseline["vib_y"] + random.uniform(-0.1, 0.1) + (wear_vib * 0.8)
        v_z = self.baseline["vib_z"] + random.uniform(-0.1, 0.1) + (wear_vib * 0.6)
        v_rms = math.sqrt(v_x**2 + v_y**2 + v_z**2)

        temp = self.baseline["temp"] + (wear_f * 40.0) + (v_rms * 0.3)
        curr = self.baseline["current"] + (wear_f * 5.0)
        pres = self.baseline["pressure"] - (wear_f * 1.5)
        rpm = self.baseline["rpm"] - int(wear_f * 50)

        return v_x, v_y, v_z, v_rms, temp, curr, pres, rpm

    def apply_chaos(self, v_x, v_rms, t, p, curr, rpm):
        # Chaos engine: introduce anomalie random indipendenti dall'usura
        if random.random() < 0.02: v_x += 10.0; v_rms += 8.0 # Vibrazione
        if random.random() < 0.01: t += 15.0 # Picco calore
        return v_x, v_rms, t, p, curr, rpm

    def run(self):
        try:
            self.client.connect(self.broker, self.port)
            print(f"🚀 [{self.pump_id}] MODE: {self.mode} | Interval: {self.interval}s")
            
            while True:
                self.update_degradation()
                v_x, v_y, v_z, v_rms, t, curr, p, rpm = self.generate_data()
                v_x, v_rms, t, p, curr, rpm = self.apply_chaos(v_x, v_rms, t, p, curr, rpm)

                payload = {
                    "measurement_id": self.cycle_count,
                    "device_id": self.pump_id,
                    "vibration_x": round(v_x, 2),
                    "vibration_y": round(v_y, 2),
                    "vibration_z": round(v_z, 2),
                    "vibration_rms": round(v_rms, 2),
                    "temperature": round(t, 1),
                    "current": round(curr, 2),
                    "pressure": round(p, 2),
                    "rpm": int(rpm),
                    "health_debug": round(self.health_percent, 1) # Utile per monitorare i test
                }

                self.client.publish(self.topic, json.dumps(payload))
                
                # Feedback a console per capire lo stato del test
                if self.cycle_count % 10 == 0:
                    print(f"📊 [{self.pump_id}] Life: {self.cycle_count}/{self.total_life_cycles} | Health: {self.health_percent:.1f}%")
                
                time.sleep(self.interval)
        except Exception as e:
            print(f"❌ [{self.pump_id}] Error: {e}")

if __name__ == "__main__":
    BROKER = os.getenv("MQTT_BROKER", "172.17.0.1")
    PORT = int(os.getenv("MQTT_PORT", 1883))
    MODE = os.getenv("SIMULATION_MODE", "NOMINAL")
    NUM_PUMPS = int(os.getenv("NUM_PUMPS", 5))

    threads = []
    for i in range(NUM_PUMPS):
        p_id = f"PUMP-{i+1:03d}"
        sim = PumpSimulator(p_id, BROKER, PORT, "factory/pumps", mode=MODE)
        t = threading.Thread(target=sim.run)
        t.daemon = True
        t.start()
        threads.append(t)
        time.sleep(0.5)

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Simulazione interrotta.")