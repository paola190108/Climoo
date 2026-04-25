from dataclasses import dataclass
from typing import Optional
from core.weather import WeatherData

@dataclass
class Alert:
    title   : str
    message : str
    level   : str   
    emoji   : str

class AlertEngine:

    def __init__(self, thresholds: dict):
        self.thresholds   = thresholds
        self._last_temp   : Optional[float] = None
        self._last_state  : Optional[str]   = None
        self._alerted_uv  : bool = False
        self._last_city   : Optional[str]   = None

    def reset(self):
        self._last_temp  = None
        self._last_state = None
        self._alerted_uv = False

    # ========================================================

    def evaluate(self, wd: WeatherData) -> Optional[Alert]:
        alert = None

        # Tempestade de raios
        if wd.state == "storm" and self._last_state != "storm":
            alert = Alert(
                title   = "Tempestade se Aproximando!",
                message = f"Alerta de tempestade em {wd.city}.\nFique em local seguro!",
                level   = "danger",
                emoji   = "⛈️",
            )

        # Chuva forte
        elif wd.rain_1h >= self.thresholds["heavy_rain_mm"] and self._last_state != "rain":
            alert = Alert(
                title   = "Chuva Intensa!",
                message = f"{wd.rain_1h} mm/h em {wd.city}.\nNão esqueça o guarda-chuva!",
                level   = "warning",
                emoji   = "🌧️",
            )

        # Vento forte
        elif wd.wind_speed_kmh >= self.thresholds["wind_speed_kmh"]:
            alert = Alert(
                title   = "Vento Forte!",
                message = f"Rajadas de {wd.wind_speed_kmh} km/h em {wd.city}.\nCuidado lá fora!",
                level   = "warning",
                emoji   = "🌬️",
            )

        # UV alto
        elif wd.uv_index >= self.thresholds["uv_index"] and not self._alerted_uv:
            alert = Alert(
                title   = "☀️ UV Muito Alto!",
                message = f"Índice UV {wd.uv_index:.0f} em {wd.city}.\nPasse protetor solar, lindeza!",
                level   = "warning",
                emoji   = "🌞",
            )
            self._alerted_uv = True

        # Reseta indicador UV quando UV baixa
        if wd.uv_index < self.thresholds["uv_index"]:
            self._alerted_uv = False

        # Guarda estado atual para próxima comparação
        self._last_temp  = wd.temp
        self._last_state = wd.state

        return alert