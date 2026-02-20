from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class SensorData(BaseModel):
    vibration_x: float = Field(..., ge=0, le=50)
    vibration_y: float = Field(..., ge=0, le=50)
    vibration_z: float = Field(..., ge=0, le=50)
    vibration_rms: float = Field(..., ge=0, le=100)
    temperature: float = Field(..., ge=0, le=150)
    current: float = Field(..., ge=0, le=50)
    pressure: float = Field(..., ge=0, le=20)
    rpm: int = Field(..., ge=0, le=10000)

class TelemetryPayload(BaseModel):
    measurement_id: int
    esp_uptime: int
    device_id: str
    operating_hours: int
    sensors: SensorData

class GroundTruthPayload(BaseModel):
    measurement_id: int
    esp_uptime: int
    device_id: str
    health_percent: float = Field(..., ge=0, le=100)
    rul_hours: int = Field(..., ge=0)
    state: Literal["HEALTHY", "WARNING", "CRITICAL", "FAILURE"]
    failure_mode: str
    life_consumed_pct: float = Field(..., ge=0, le=100)

class MergedDataPoint(BaseModel):
    """Dato completo dopo il merge - TUTTI i campi required tranne i metadati opzionali"""
    measurement_id: int
    device_id: str
    timestamp_received: datetime = Field(default_factory=datetime.utcnow)
    
    operating_hours: int
    sensors: SensorData
    
    health_percent: float
    rul_hours: int
    state: Literal["HEALTHY", "WARNING", "CRITICAL", "FAILURE"]
    failure_mode: str
    life_consumed_pct: float
    
    # Solo questi sono opzionali
    esp_uptime_telemetry: Optional[int] = None
    esp_uptime_truth: Optional[int] = None
