import requests
import logging
from dataclasses import dataclass, field
from typing import Optional, List

logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    city          : str   = ""
    temp          : float = 0.0
    feels_like    : float = 0.0
    humidity      : int   = 0
    description   : str   = ""
    icon_code     : int   = 0
    wind_speed    : float = 0.0
    wind_speed_kmh: float = 0.0
    uv_index      : float = 0.0
    rain_1h       : float = 0.0
    snow_1h       : float = 0.0
    alerts        : List[str] = field(default_factory=list)
    state         : str   = "default"
    raw           : dict  = field(default_factory=dict)


# Mapeamento de WMO weather codes
# https://open-meteo.com/en/docs#weathervariables
WMO_MAP = {
    0 : ("Céu limpo",           "sunny"),
    1 : ("Principalmente limpo","sunny"),
    2 : ("Parcialmente nublado","cloudy"),
    3 : ("Nublado",             "cloudy"),
    45: ("Neblina",             "cloudy"),
    48: ("Neblina com geada",   "cloudy"),
    51: ("Chuvisco leve",       "rain"),
    53: ("Chuvisco moderado",   "rain"),
    55: ("Chuvisco intenso",    "rain"),
    61: ("Chuva leve",          "rain"),
    63: ("Chuva moderada",      "rain"),
    65: ("Chuva forte",         "rain"),
    71: ("Neve leve",           "snow"),
    73: ("Neve moderada",       "snow"),
    75: ("Neve intensa",        "snow"),
    77: ("Granizo",             "snow"),
    80: ("Pancadas de chuva",   "rain"),
    81: ("Pancadas moderadas",  "rain"),
    82: ("Pancadas fortes",     "rain"),
    85: ("Pancadas de neve",    "snow"),
    86: ("Pancadas de neve int","snow"),
    95: ("Tempestade",          "storm"),
    96: ("Tempestade c/ granizo","storm"),
    99: ("Tempestade intensa",  "storm"),
}


class WeatherFetcher:
    GEO_URL     = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, api_key: str = "", city: str = "São Paulo",
                 units: str = "metric", cfg=None):
        self._city  = city
        self._units = units
        self._cfg   = cfg
        self._geo_cache: dict = {} 

    @property
    def city(self):
        return self._cfg.CITY if self._cfg else self._city

    @property
    def units(self):
        return self._cfg.UNITS if self._cfg else self._units

    # ==========================================================
    
    def fetch(self) -> Optional[WeatherData]:
        try:
            lat, lon, city_name = self._geocode(self.city)
            if lat is None:
                return None
            return self._fetch_weather(lat, lon, city_name)
        except requests.exceptions.ConnectionError:
            logger.warning("Sem internet. Tentando novamente em breve...")
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
        return None

    # ==========================================================
    
    def _geocode(self, city: str):
        if city in self._geo_cache:
            return self._geo_cache[city]

        resp = requests.get(self.GEO_URL, params={
            "name": city, "count": 1, "language": "pt", "format": "json"
        }, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("results"):
            logger.error(f"Cidade não encontrada: {city}")
            return None, None, city

        r = data["results"][0]
        result = (r["latitude"], r["longitude"],
                  f"{r['name']}, {r.get('country', '')}")
        self._geo_cache[city] = result
        return result

    # ==========================================================
    
    def _fetch_weather(self, lat, lon, city_name) -> WeatherData:
        temp_unit = "celsius" if self.units == "metric" else "fahrenheit"

        params = {
            "latitude"           : lat,
            "longitude"          : lon,
            "current"            : [
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "wind_speed_10m",
                "weather_code",
                "precipitation",
                "snowfall",
                "uv_index",
            ],
            "temperature_unit"   : temp_unit,
            "wind_speed_unit"    : "kmh",
            "precipitation_unit" : "mm",
            "timezone"           : "auto",
        }

        resp = requests.get(self.WEATHER_URL, params=params, timeout=10)
        resp.raise_for_status()
        raw = resp.json()
        cur = raw["current"]

        wmo_code    = cur.get("weather_code", 0)
        description, state = WMO_MAP.get(wmo_code, ("Sem dados", "default"))
        wind_kmh    = cur.get("wind_speed_10m", 0)

        wd = WeatherData(
            city          = city_name,
            temp          = cur.get("temperature_2m", 0),
            feels_like    = cur.get("apparent_temperature", 0),
            humidity      = int(cur.get("relative_humidity_2m", 0)),
            description   = description,
            icon_code     = wmo_code,
            wind_speed    = round(wind_kmh / 3.6, 2),
            wind_speed_kmh= round(wind_kmh, 1),
            uv_index      = cur.get("uv_index", 0),
            rain_1h       = cur.get("precipitation", 0),
            snow_1h       = cur.get("snowfall", 0),
            state         = state,
            raw           = raw,
        )
        return wd