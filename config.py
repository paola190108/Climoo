from dotenv import load_dotenv
import os

load_dotenv()

CITY  = os.getenv("CITY", "São Paulo")
UNITS = os.getenv("UNITS", "metric")                

# Intervalos de atualização
UPDATE_INTERVAL_MS  = 3 * 60 * 1000   
BLINK_INTERVAL_MS   = 800              

# Geometria da janela 
WINDOW_WIDTH  = 260
WINDOW_HEIGHT = 160
MARGIN        = 18          


# Paleta pastel
PALETTE = {
    # Estado padrão (céu limpo)
    "default_bg"       : "#FFE4F0",   
    "default_fg"       : "#C2607A",   
    "default_accent"   : "#FFB7D5",  

    # Ensolarado
    "sunny_bg"         : "#B8E8FF",   
    "sunny_fg"         : "#1A6EA8",   
    "sunny_accent"     : "#7DCFFF",   

    # Nublado
    "cloudy_bg"        : "#DDE8F5",   
    "cloudy_fg"        : "#5A7A9E",
    "cloudy_accent"    : "#B8CCE4",

    # Chuva
    "rain_bg"          : "#C8D8F0",   
    "rain_fg"          : "#2C4F7C",
    "rain_accent"      : "#8AAED4",

    # Tempestade
    "storm_bg"         : "#E8D0F5",  
    "storm_fg"         : "#6A2E8C",
    "storm_accent"     : "#C490E8",

    # UV Alto
    "uv_bg"            : "#FFF3B0",   
    "uv_fg"            : "#A07800",
    "uv_accent"        : "#FFE44D",

    # Neve
    "snow_bg"          : "#EEF4FF",
    "snow_fg"          : "#3A5A9E",
    "snow_accent"      : "#C4D8FF",

    # Botão fechar
    "close_btn"        : "#FFB7D5",
    "close_hover"      : "#FF8FB3",
}

# Limites para pop-up de alerta

ALERT_THRESHOLDS = {
    "wind_speed_kmh"   : 50,    # Vento acima de 50 km/h → alerta
    "uv_index"         : 8,     # UV acima de 8 → alerta
    "temp_change_c"    : 6,     # Mudança de +/-6 °C em 10 min → alerta
    "heavy_rain_mm"    : 10,    # Chuva > 10 mm/h → alerta
}

WEATHER_STATES = {
    range(200, 300): "storm",    # Tempestades elétricas
    range(300, 400): "rain",     # Chuvisco
    range(500, 600): "rain",     # Chuva
    range(600, 700): "snow",     # Neve
    range(700, 800): "cloudy",   # Névoa / neblina
    range(800, 801): "sunny",    # Céu limpo
    range(801, 900): "cloudy",   # Nublado
}