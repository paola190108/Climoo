import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.app import WeatherBotApp

if __name__ == "__main__":
    app = WeatherBotApp()
    app.run()
