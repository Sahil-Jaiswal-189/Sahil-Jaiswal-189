"""Generate a compact Pune weather snapshot for the profile README."""
import json
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.request import urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
URL = ('https://api.open-meteo.com/v1/forecast?latitude=18.5204&longitude=73.8567'
       '&current=temperature_2m,weather_code,is_day'
       '&timezone=Asia%2FKolkata')


def describe(code):
    if code == 0:
        return 'Clear sky', 'clear'
    if code in (1, 2):
        return 'Partly cloudy', 'partial'
    if code == 3:
        return 'Cloudy', 'cloud'
    if code in (45, 48):
        return 'Foggy', 'fog'
    if code in (51, 53, 55, 56, 57):
        return 'Drizzle', 'rain'
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return 'Rainy', 'rain'
    if code in (71, 73, 75, 77, 85, 86):
        return 'Snow', 'snow'
    if code in (95, 96, 99):
        return 'Thunderstorm', 'storm'
    return 'Unknown conditions', 'unknown'


def render(now, current=None):
    available = current is not None
    day = bool(current['is_day']) if available else None
    label, kind = describe(current['weather_code']) if available else ('Weather unavailable', 'unknown')
    accent = '#ffd38a' if day else '#c5bdff'
    period = ('Daytime' if day else 'Nighttime') if available else 'Day/night unavailable'
    temp = current['temperature_2m'] if available else None
    temperature = f'{temp:.0f}°C' if available else '—'
    # Descriptive bands for this widget, not meteorological or health thresholds.
    band = ('Cold' if temp < 15 else 'Cool' if temp < 22 else 'Mild' if temp < 28
            else 'Warm' if temp < 33 else 'Hot') if available else 'No reading'
    color = ('#84caff' if temp < 22 else '#a5e6bc' if temp < 28
             else '#ffcf82' if temp < 33 else '#ff9f91') if available else '#8c96ad'
    cloud = '<path d="M-21 8 H17 A12 12 0 0 0 17 -16 A17 17 0 0 0 -13 -19 A13 13 0 0 0 -21 8" fill="#c1cee4"/>'
    sun = '<circle cx="0" cy="-9" r="15" fill="#ffd38a"/>'
    moon = '<path d="M5 -25 A17 17 0 1 0 15 -1 A18 18 0 0 1 5 -25" fill="#d6d0ff"/>'
    icon = sun if day else moon
    if kind in ('cloud', 'fog', 'rain', 'snow', 'storm'):
        icon = cloud
    elif kind == 'partial':
        icon = f'<g transform="translate(10,-8)">{icon}</g>{cloud}'
    elif kind == 'unknown':
        icon = '<text x="-8" y="3" fill="#98a6bf" font-size="26">?</text>'
    if kind == 'rain':
        icon += '<path d="M-13 16 l-3 7 M0 16 l-3 7 M13 16 l-3 7" stroke="#82bcff" stroke-width="3" stroke-linecap="round"/>'
    elif kind == 'storm':
        icon += '<path d="M2 10 l-9 15 h8 l-3 10 14-18 H4 l4-7" fill="#ffcf82"/>'
    elif kind == 'fog':
        icon += '<path d="M-20 17 H20 M-14 24 H14" stroke="#9cacc7" stroke-width="3" stroke-linecap="round"/>'
    elif kind == 'snow':
        icon += '<g fill="#d8eeff"><circle cx="-12" cy="20" r="2"/><circle cy="25" r="2"/><circle cx="12" cy="20" r="2"/></g>'
    pill_width = 158 if not available else 84
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="228" viewBox="0 0 480 228" role="img" aria-label="{escape('Pune weather: ' + temperature + ', ' + label + ', ' + period + ', ' + now.strftime('%d %b %Y'))}">
<defs>
  <linearGradient id="card" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#192234"/><stop offset="1" stop-color="#101722"/></linearGradient>
  <radialGradient id="glow"><stop stop-color="{accent}" stop-opacity=".14"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
</defs>
<rect x=".5" y=".5" width="479" height="227" rx="20" fill="url(#card)" stroke="#303b50"/>
<g font-family="Verdana,Arial,sans-serif">
<text x="26" y="32" font-size="9" letter-spacing="2.4" fill="#99a9c0">CURRENT WEATHER</text>
<g transform="translate({454-pill_width},19)">
  <rect width="{pill_width}" height="24" rx="12" fill="{accent}" fill-opacity=".09"/>
  <circle cx="12" cy="12" r="2.5" fill="{accent}"/>
  <text x="21" y="16" font-size="9" fill="{accent}">{period}</text>
</g>
<path d="M29 52 a4 4 0 1 0 0 8 a4 4 0 1 0 0 -8 M26 60 l3 4 3-4" fill="none" stroke="#aebcd0" stroke-width="1.2"/>
<text x="42" y="63" font-size="13" fill="#d8e1ee">Pune, India</text>
<text x="24" y="128" font-size="54" font-weight="700" letter-spacing="-2" fill="#f3f6fc">{temperature}</text>
<text x="27" y="156" font-size="14" fill="#d1dcec">{escape(label)}</text>
<circle cx="30" cy="176" r="3" fill="{color}"/>
<text x="40" y="180" font-size="10" fill="{color}">{band}</text>
<circle cx="373" cy="112" r="73" fill="url(#glow)"/>
<circle cx="373" cy="112" r="48" fill="none" stroke="{accent}" stroke-opacity=".08"/>
<g transform="translate(373,118) scale(1.65)">{icon}</g>
<path d="M26 195 H454" stroke="#2b3648"/>
<text x="26" y="215" font-size="9" fill="#9cacc1">{now.strftime('%a, %d %b %Y')}</text>
<text x="454" y="215" text-anchor="end" font-size="8" fill="#8999b0">Hourly snapshot · Open-Meteo</text>
</g></svg>'''



def main():
    current = None
    try:
        with urlopen(URL, timeout=25) as response:
            current = json.load(response)['current']
        for key in ('temperature_2m', 'weather_code', 'is_day'):
            if current.get(key) is None:
                raise ValueError('Missing weather field: ' + key)
    except Exception as error:
        print('Weather unavailable:', type(error).__name__)
        current = None
    svg = render(datetime.now(ZoneInfo('Asia/Kolkata')), current)
    (ROOT / 'assets').mkdir(exist_ok=True)
    (ROOT / 'assets/pune-dashboard.svg').write_text(svg, encoding='utf-8')


if __name__ == '__main__':
    main()
