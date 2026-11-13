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
    hour_angle = ((now.hour % 12) + now.minute / 60) * 30
    minute_angle = now.minute * 6
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="226" viewBox="0 0 500 226" role="img" aria-label="{escape('Pune weather: ' + temperature + ', ' + label + ', ' + period + '. Time snapshot ' + now.strftime('%I:%M %p IST'))}">
<rect x=".5" y=".5" width="499" height="225" rx="18" fill="#111827" stroke="#30394c"/>
<g font-family="Verdana,Arial,sans-serif">
<text x="24" y="32" font-size="10" letter-spacing="2" fill="#a3b0c5">CURRENT WEATHER</text>
<text x="24" y="57" font-size="13" fill="#dbe4f2">Pune, India</text>
<g transform="translate(48,108) scale(.9)">{icon}</g>
<text x="85" y="121" font-size="42" font-weight="700" fill="{color}">{temperature}</text>
<text x="24" y="153" font-size="14" fill="#e1e8f5">{escape(label)}</text>
<text x="24" y="176" font-size="11" fill="{accent}">{period} · {band}</text>
<path d="M270 27 V181" stroke="#30394c"/>
<g transform="translate(377,76)">
<circle r="34" fill="#1c2639" stroke="#566079"/>
<path d="M0 -28 V-24 M28 0 H24 M0 28 V24 M-28 0 H-24" stroke="#b4bfd1" stroke-width="2"/>
<path d="M0 3 V-16" transform="rotate({hour_angle})" stroke="#e4eaf5" stroke-width="3.5" stroke-linecap="round"/>
<path d="M0 4 V-24" transform="rotate({minute_angle})" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>
<circle r="3" fill="{accent}"/>
</g>
<text x="377" y="137" text-anchor="middle" font-size="23" font-weight="700" fill="#f0f4fb">{now.strftime('%I:%M %p')}</text>
<text x="377" y="158" text-anchor="middle" font-size="11" fill="#b0bdd2">{now.strftime('%a, %d %b %Y')}</text>
<text x="377" y="178" text-anchor="middle" font-size="10" fill="#95a5bd">IST · UTC +05:30</text>
<path d="M24 192 H476" stroke="#273247"/>
<text x="24" y="212" font-size="9" fill="#8f9fb7">Snapshot {now.strftime('%H:%M')} IST · Hourly refresh · Weather: Open-Meteo</text>
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
