# Climoo
Um bot meteorológico minimalista que flutua na sua área de trabalho com alertas automáticos de clima em tempo real.

## Descrição
O Cutesy Weather Alert Bot é uma aplicação desktop desenvolvida em Python que exibe as condições climáticas atuais em uma janela flutuante e sem bordas no canto da tela. O design segue uma estética cutesy com paleta de cores pastel.

--- 

## Tecnologias utilizadas
- Linguagem: Python 
- Interface gráfica: Tkinter (nativo)
- API meteorológica: Open-Meteo (gratuita, sem chave)
- Geocodificação: Open-Meteo Geocoding API
- Empacotamento: PyInstaller

---

## Funcionalidades
- Janela flutuante sem bordas, arrastável, sempre no topo
- Estados visuais dinâmicos conforme o clima (sol, chuva, tempestade, neve, UV)
- PopUps automáticos de alerta para: tempestades, chuva intensa, vento forte e UV alto
- Painel de configurações com seletor de cidade, unidade (°C/°F) e seletor de coloração para personalizar a cor de fundo

---

## Aprendizados
Neste projeto desenvolvi uma aplicação desktop completa em Python utilizando Tkinter para construir uma interface gráfica customizada do zero — sem frameworks externos de UI. Aprendi a desenhar elementos visuais diretamente em Canvas (estrelas, corações, animações, gotas de chuva), gerenciar threads para não travar a interface durante chamadas de API, consumir APIs REST com geocodificação automática, persistir configurações com variáveis de ambiente e empacotar a aplicação como executável multiplataforma com PyInstaller e GitHub Actions.

---

##  Como executar
**1. Clone o repositório:**
```bash
git clone https://github.com/SEU_USUARIO/cutesy-weather-bot
cd cutesy-weather-bot
```
 
**2. Crie e ative o ambiente virtual:**
```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows
```
 
**3. Instale as dependências:**
```bash
pip install -r requirements.txt
```
 
**4. Configure sua cidade no `.env`:**
```bash
cp .env.example .env
```
Edite o `.env` com sua cidade:
```
CITY=São Paulo
UNITS=metric
```
 
**5. Execute:**
```bash
python main.py
```
---

## Executável
 
Baixe o executável pronto na aba [Releases](../../releases) — sem precisar de Python instalado.
 
| Sistema | Arquivo |
|---|---|
| Windows | `WeatherBot.exe` |
| Linux | `WeatherBot` |
 


