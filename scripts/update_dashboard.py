"""Generate a compact Pune weather snapshot for the profile README."""
import json
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.request import urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
URL = ('https://api.open-meteo.com/v1/forecast?latitude=18.5204&longitude=73.8567'
       '&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,is_day'
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
    sky = '#263e54' if day else '#22243f'
    accent = '#ffd38a' if day else '#c5bdff'
    period = ('Daytime' if day else 'Nighttime') if available else 'Day/night unavailable'
    temp = current['temperature_2m'] if available else None
    temperature = f'{temp:.0f}°C' if available else '—'
    # Descriptive bands for this widget, not meteorological or health thresholds.
    band = ('Cold' if temp < 15 else 'Cool' if temp < 22 else 'Mild' if temp < 28
            else 'Warm' if temp < 33 else 'Hot') if available else 'No reading'
    color = ('#84caff' if temp < 22 else '#a5e6bc' if temp < 28
             else '#ffcf82' if temp < 33 else '#ff9f91') if available else '#8c96ad'
    summary = (f"Feels {current['apparent_temperature']:.0f}° · Humidity {current['relative_humidity_2m']:.0f}%"
               if available else 'Waiting for the next weather refresh')
    celestial = ('<circle cx="132" cy="39" r="13" fill="#ffd38a"/>' if day else
                 '<path d="M140 26 A14 14 0 1 0 145 48 A15 15 0 0 1 140 26" fill="#d6d0ff"/>') if available else ''
    stars = '' if day or not available else '<g fill="#a8a7ce"><circle cx="28" cy="33" r="1.5"/><circle cx="73" cy="24" r="1"/><circle cx="109" cy="63" r="1.5"/></g>'
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
    position = max(0, min(100, (temp + 5) / 50 * 100)) if available else 0
    thermometer = f'<circle cx="{416 + position:.1f}" cy="75" r="4" fill="{color}"/>' if available else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="620" height="184" viewBox="0 0 620 184" role="img" aria-label="{escape(period + ', Pune: ' + temperature + ', ' + label)}">
<defs><linearGradient id="heat"><stop stop-color="#84caff"/><stop offset=".5" stop-color="#a5e6bc"/><stop offset="1" stop-color="#ff9f91"/></linearGradient><clipPath id="art"><rect x="12" y="12" width="160" height="160" rx="12"/></clipPath></defs>
<rect x=".5" y=".5" width="619" height="183" rx="16" fill="#111827" stroke="#30394c"/>
<g font-family="Verdana,Arial,sans-serif">
<g clip-path="url(#art)"><rect x="12" y="12" width="160" height="160" fill="{sky}"/>{stars}{celestial}
<path d="M12 110 Q50 62 94 110 Q140 75 172 100 V172 H12Z" fill="#39475b"/>
<g fill="#bc8d7c" stroke="#222b3e" stroke-width="2"><path d="M26 146 V111 H49 V91 H66 V111 H118 V91 H135 V111 H158 V146Z"/><path d="M49 91 L57 80 L66 91 M118 91 L126 80 L135 91" fill="#e2b096"/><path d="M77 146 V125 Q92 105 107 125 V146Z" fill="#222b3e"/></g>
<rect x="12" y="146" width="160" height="26" fill="#1d293d"/><text x="92" y="164" text-anchor="middle" fill="#d4dbea" font-size="10" letter-spacing="3">PUNE</text></g>
<text x="190" y="31" font-size="10" fill="{accent}" letter-spacing="1.5">A LITTLE PUNE CHECK-IN</text>
<text x="190" y="65" font-size="27" fill="#eff3fb" font-weight="700">{now.strftime('%I:%M %p')}</text>
<text x="190" y="87" font-size="11" fill="#b3bfd4">{now.strftime('%a, %d %b %Y')} · IST</text>
<circle cx="195" cy="108" r="3" fill="{accent}"/><text x="205" y="112" font-size="11" fill="{accent}">{period}</text>
<path d="M382 38 V119" stroke="#30394c"/>
<text x="404" y="61" font-size="25" font-weight="700" fill="{color}">{temperature}</text>
<text x="488" y="58" font-size="11" fill="{color}">{band}</text>
<rect x="416" y="73" width="100" height="4" rx="2" fill="url(#heat)"/>{thermometer}
<g transform="translate(567,65) scale(.8)">{icon}</g>
<text x="404" y="104" font-size="12" fill="#e0e7f5">{escape(label)}</text>
<text x="190" y="138" font-size="10" fill="#aab8ce">{escape(summary)}</text>
<text x="190" y="158" font-size="9" fill="#8594ac">Snapshot {now.strftime('%H:%M')} IST · Hourly refresh · Open-Meteo</text>
</g></svg>'''


def main():
    current = None
    try:
        with urlopen(URL, timeout=25) as response:
            current = json.load(response)['current']
        for key in ('temperature_2m', 'apparent_temperature', 'relative_humidity_2m', 'weather_code', 'is_day'):
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
