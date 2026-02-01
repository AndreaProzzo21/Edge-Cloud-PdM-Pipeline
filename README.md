# 🏭 Predictive Maintenance Pipeline

## 🎯 Obiettivo

Progettazione e implementazione di una pipeline completa per **Predictive Maintenance** (manutenzione predittiva) su una pompa centrifuga industriale. Il sistema raccoglie dati fisiologici della macchina, li archivia in serie temporali e prepara dataset strutturati per l'addestramento di modelli ML (anomaly detection, regressione RUL - Remaining Useful Life).

**Stato attuale**: Fase 1 (Data Collection & Storage) ✓  
**Prossima milestone**: Fase 2 (Feature Engineering, Training e Validazione modelli)

## 📦 Stack Tecnologico

| Componente | Tecnologia | Ruolo |
| --- | --- | --- |
| **Edge Device** | ESP32 | Generazione dati e serializzazione |
| **Protocollo** | MQTT (Paho) | Transport layer con QoS 1 (at least once) |
| **Buffering** | Threading Queue | Decoupling tra acquisizione e storage |
| **Validation** | Pydantic v2 | Schema enforcement e Type safety |
| **Storage** | InfluxDB 2.7 | Database ottimizzato per serie temporali |
| **Orchestration** | Docker Compose | Networking isolata per l'intero stack |

---

[![Docker Compose](https://img.shields.io/badge/Docker-Compose-blue)](https://docs.docker.com/compose/)
[![MQTT](https://img.shields.io/badge/Protocol-MQTT-orange)](https://mqtt.org/)
[![InfluxDB](https://img.shields.io/badge/DB-InfluxDB%202.x-red)](https://www.influxdata.com/)


## Data acquisition

Invece di usare dataset publici fittizi, ho simulato una pompa centrifuga industriale con ESP32. I dati seguono curve di usura realistiche (Weibull) e correlazioni fisiche reali (ISO 10816 per le vibrazioni). In tal modo posso avere maggiore controllo sulla ground truth al fine di validare meglio i modelli ML nella Fase 2. 

## Architettura attuale

**Edge**: ESP32 genera due topic MQTT sincronizzati via `measurement_id`:
- `factory/pump001/telemetry`: sensori grezzi (vibrazioni 3 assi, temp, corrente, pressione)
- `factory/pump001/ground_truth`: stato salute, RUL, classe di failure

**Pipeline**: Container Python che:
1. Sottoscrive entrambi i topic (Paho MQTT)
2. Merge tramite Buffer (evita perdita pacchetti se uno dei due topic lagga)
3. Validazione schema (Pydantic)
4. Storage su InfluxDB (batch write con retry automatico)
5. Export CSV per training (script separato)

**Broker & DB**: Mosquitto e InfluxDB in container Docker separati, rete bridge dedicata.

## Parametri fisici implementati

- **Vibrazioni**: mm/s RMS ISO 10816. Asse X orizzontale più affetto da wear (cuscinetti).
- **Termodinamica**: temperatura cuscinetti correlata all'attrito (quindi alle vibrazioni).
- **Elettrica**: corrente assorbita sale quando l'efficienza meccanica cala (usura girante/tenute).
- **Idraulica**: pressione in calo quando l'impulsore si consuma.

La degradazione non è lineare: fase iniziale lenta, accelerazione esponenziale dopo il 70% di vita utile consumata.

## 📊 Esempio Dati Export (Training Set)

Il comando `python scripts/export_training_data.py` genera un output strutturato pronto per Scikit-Learn o XGBoost:

| timestamp | vibration_rms | temp |current | health_percent | state |
| --- | --- | --- | --- | --- | --- |
| 2026-02-01T10:00Z | 1.87 | 42.2 | 8.18 | 100.0 | HEALTHY |
| 2026-02-01T20:00Z | 8.32 | 78.5 | 11.2 | 12.0 | CRITICAL |

---

## 🛤️ Roadmap di Sviluppo

* [x] **Fase 1: Data Strategy and Acquisition**
* Simulazione fisica, Protocollo MQTT, Storage InfluxDB.


* [ ] **Fase 2: Intelligence, training and validation**
* Feature Engineering, Training Isolation Forest e Random Forest.


* [ ] **Fase 3: Deployment**


## 📄 Note 

I dati sono generati sinteticamente a scopo di ricerca, calibrati secondo gli standard **ISO 10816** e **API 610**.


