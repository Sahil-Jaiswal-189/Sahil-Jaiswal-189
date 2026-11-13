import json
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.request import urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
now = datetime.now(ZoneInfo('Asia/Kolkata'))
weather, detail = 'Unavailable', 'Try again on the next update'
url = ('https://api.open-meteo.com/v1/forecast?latitude=18.5204&longitude=73.8567'
       '&current=temperature_2m,weather_code&timezone=Asia%2FKolkata')
try:
    with urlopen(url, timeout=25) as response:
        current = json.load(response)['current']
    code = current['weather_code']
    conditions = {0: 'Clear sky', 1: 'Mostly clear', 2: 'Partly cloudy', 3: 'Overcast',
                  45: 'Fog', 48: 'Rime fog', 51: 'Light drizzle', 53: 'Drizzle',
                  55: 'Heavy drizzle', 56: 'Freezing drizzle', 57: 'Freezing drizzle',
                  61: 'Light rain', 63: 'Rain', 65: 'Heavy rain', 66: 'Freezing rain',
                  67: 'Freezing rain', 71: 'Light snow', 73: 'Snow', 75: 'Heavy snow',
                  77: 'Snow grains', 80: 'Light showers', 81: 'Showers', 82: 'Heavy showers',
                  85: 'Snow showers', 86: 'Heavy snow showers', 95: 'Thunderstorm',
                  96: 'Thunderstorm with hail', 99: 'Thunderstorm with hail'}
    weather = f"{current['temperature_2m']:.0f} °C"
    detail = conditions.get(code, 'Weather code ' + str(code))
except Exception as error:
    print('Weather unavailable:', type(error).__name__)

def card(x, label, value, subtitle):
    return f'''<g transform="translate({x},330)">
    <rect width="280" height="130" rx="18" fill="#161d35" stroke="#303a5f"/>
    <text x="22" y="30" fill="#b6a2ff" font-size="12" letter-spacing="2">{escape(label)}</text>
    <text x="22" y="74" fill="#f8fafc" font-size="30" font-weight="700">{escape(value)}</text>
    <text x="22" y="104" fill="#a9b5d3" font-size="13">{escape(subtitle)}</text></g>'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="520" viewBox="0 0 960 520" role="img" aria-label="Pune skyline and local time, date and weather dashboard">
<defs><linearGradient id="sky" x2="1" y2="1"><stop stop-color="#211743"/><stop offset="1" stop-color="#101e38"/></linearGradient></defs>
<rect width="960" height="520" rx="24" fill="#0d1224"/>
<rect x="20" y="20" width="920" height="285" rx="18" fill="url(#sky)"/>
<g font-family="Verdana,Arial,sans-serif">
<text x="52" y="67" fill="#c2afff" font-size="12" letter-spacing="4">A LITTLE CORNER OF MY WORLD</text>
<text x="50" y="132" fill="#ffffff" font-size="58" font-weight="700">PUNE</text>
<text x="53" y="163" fill="#d4d9ed" font-size="16">Maharashtra, India · Building, learning, contributing.</text>
<circle cx="826" cy="85" r="34" fill="#ffcda3"/>
<path d="M20 268 Q160 170 300 260 Q430 184 580 267 Q750 170 940 255 V305 H20Z" fill="#343759"/>
<!-- Stylized illustration inspired by Shaniwar Wada; not a photograph. -->
<g fill="#d19685" stroke="#281e35" stroke-width="3">
<path d="M370 294 V237 H395 V211 H429 V237 H530 V211 H564 V237 H590 V294Z"/>
<path d="M395 211 L412 195 L429 211 M530 211 L547 195 L564 211" fill="#ffcda3"/>
<path d="M448 294 V262 Q480 219 512 262 V294Z" fill="#231e36"/>
<path d="M300 294 V264 H370 V294 M590 294 V264 H665 V294"/>
</g>
<g fill="#121a30"><path d="M45 294 V251 H75 V231 H106 V294 M130 294 V242 H169 V294 M690 294 V224 H731 V294 M748 294 V247 H784 V294 M852 294 V229 H893 V294"/></g>
<text x="53" y="287" fill="#cad3eb" font-size="10">PUNE · ILLUSTRATED SKYLINE</text>
{card(40, 'LOCAL TIME', now.strftime('%I:%M %p'), 'IST · UTC +05:30 · snapshot')}
{card(340, 'TODAY IN PUNE', now.strftime('%d %b %Y'), now.strftime('%A'))}
{card(640, 'PUNE WEATHER', weather, detail)}
<text x="40" y="493" fill="#8c9bbd" font-size="11">Updated {now.strftime('%d %b %Y, %I:%M %p')} IST · Scheduled hourly · Weather: Open-Meteo</text>
</g></svg>'''
(ROOT / 'assets').mkdir(exist_ok=True)
(ROOT / 'assets/pune-dashboard.svg').write_text(svg, encoding='utf-8')
