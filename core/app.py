import threading
import logging
import time
import sys
import os

# Logging 
logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt = "%H:%M:%S",
)
logger = logging.getLogger(__name__)


class WeatherBotApp:
    def __init__(self):
        # Evita circular imports
        import config
        from core.weather import WeatherFetcher
        from core.alerts  import AlertEngine
        from ui.window    import FloatingWindow

        self.cfg         = config
        self.fetcher     = WeatherFetcher(city=config.CITY, units=config.UNITS, cfg=config)
        self.alerts      = AlertEngine(config.ALERT_THRESHOLDS)
        self.window      = FloatingWindow(config)
        self._last_city  = config.CITY
        self._last_units = config.UNITS

        # Quando a janela precisar de dados, chama _update
        self.window.set_update_callback(self._fetch_and_update)
        # Expõe alert engine para a janela resetar ao trocar cidade
        self.window._alert_engine = self.alerts

    # ==========================================================

    def run(self):
        logger.info("Cutesy Weather Bot iniciando...")
        t = threading.Thread(target=self._fetch_and_update, daemon=True)
        t.start()
        self.window.mainloop()  

    # ==========================================================
    
    def _fetch_and_update(self):
        # Reseta elementos do bot em caso de mudanças
        if self.cfg.CITY != self._last_city or self.cfg.UNITS != self._last_units:
            self.alerts.reset()
            self._last_city = self.cfg.CITY
            self._last_units = self.cfg.UNITS

        logger.info(f"Buscando clima: {self.cfg.CITY}...")
        wd = self.fetcher.fetch()

        if wd is None:
            self.window.show_error()
            return

        logger.info(
            f"{wd.city}: {wd.temp:.1f}°C, {wd.description}, "
            f"vento {wd.wind_speed_kmh} km/h, UV {wd.uv_index}"
        )

        # Atualiza janela principal 
        self.window.update_weather(wd)

        # Avalia se deve disparar PopUp
        alert = self.alerts.evaluate(wd)
        if alert:
            logger.info(f"Alerta disparado: {alert.title}")
            self.window.show_alert_popup(alert)