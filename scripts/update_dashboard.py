"""Generate a compact Pune weather snapshot for the profile README."""
import json
import math
import subprocess
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'assets/pune-weather.json'
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


def scene(day, kind):
    """Original vector artwork inspired by Pune's Shaniwar Wada."""
    wet = kind in ('rain', 'storm', 'fog', 'snow')
    sky_top = '#253447' if wet else '#222b50' if day else '#171b3c'
    sky_bottom = '#687c83' if wet else '#c39180' if day else '#515079'
    sun = ''
    if day is not None and kind in ('clear', 'partial'):
        sun = ('<circle cx="478" cy="74" r="49" fill="#ffdbab" opacity=".06"/>'
               '<circle cx="478" cy="74" r="35" fill="#ffdbab" opacity=".08"/>'
               '<circle cx="478" cy="74" r="22" fill="url(#sun)"/>' if day else
               '<circle cx="478" cy="70" r="34" fill="#c7c5ff" opacity=".05"/>'
               '<path d="M486 49 A23 23 0 1 0 498 85 A25 25 0 0 1 486 49" fill="#e1dcff"/>')
    stars = '' if day or kind not in ('clear', 'partial') or day is None else ''.join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="#d5cfff" opacity=".7"/>'
        for x, y, r in [(322,60,1),(355,83,1.4),(403,45,1),(432,91,1),(518,107,1.2),(382,25,.8)])
    clouds = ''
    if kind not in ('clear', 'unknown'):
        clouds = """<g fill="url(#cloud)" opacity=".8">
        <path d="M330 82 C319 82 318 69 328 66 C329 52 349 47 357 61 C370 55 380 65 376 75 C389 77 386 87 376 87 H333Z"/>
        <path d="M424 111 C410 111 409 94 423 91 C426 74 450 69 461 87 C478 80 490 92 486 103 C503 104 500 117 486 117 H430Z"/>
        </g>"""
    effects = ''
    if kind in ('rain', 'storm'):
        effects = '<g stroke="#b4d3e2" stroke-width="1.2" opacity=".5">' + ''.join(
            f'<path d="M{x} {y} l-4 10"/>' for x,y in [(329,96),(352,107),(380,91),(402,121),(436,126),(463,133),(495,123),(523,144),(313,131)]) + '</g>'
    if kind == 'storm':
        effects += '<path d="M469 111 l-12 20 h10 l-4 14 20-25 h-13 l6-9" fill="#ffe6a6"/>'
    if kind == 'fog':
        effects = '<g stroke="#cbd9d9" stroke-linecap="round" opacity=".35"><path d="M302 135 H414 M368 151 H534 M314 167 H490" stroke-width="5"/></g>'
    if kind == 'snow':
        effects = '<g fill="#edf6ff">' + ''.join(f'<circle cx="{x}" cy="{y}" r="1.7"/>' for x,y in [(330,103),(385,113),(440,130),(495,120),(520,148),(310,148)]) + '</g>'
    windows = ''.join(f'<path d="M{x} 163 v-8 a3 3 0 0 1 6 0 v8Z" fill="{("#493648" if day else "#ffd29b")}" opacity=".85"/>' for x in (348,366,474,492))
    return f'''<defs>
    <linearGradient id="sky" x2="0" y2="1"><stop stop-color="{sky_top}"/><stop offset="1" stop-color="{sky_bottom}"/></linearGradient>
    <linearGradient id="sun" x2="0" y2="1"><stop stop-color="#ffe9b6"/><stop offset="1" stop-color="#f4b787"/></linearGradient>
    <linearGradient id="cloud" x2="0" y2="1"><stop stop-color="#d9d9e5"/><stop offset="1" stop-color="#8e99b3"/></linearGradient>
    <linearGradient id="stone" x2="1" y2="1"><stop stop-color="#c8a08d"/><stop offset="1" stop-color="#916b6a"/></linearGradient>
    </defs>
    <g clip-path="url(#scene)">
    <path fill="url(#sky)" d="M288 12 H548 V230 H288Z"/>
    {stars}{sun}
    <path d="M288 145 Q321 114 359 129 Q398 92 437 131 Q501 93 548 127 V230 H288Z" fill="#5c6074" opacity=".6"/>
    <path d="M288 167 Q332 132 376 157 Q438 118 478 152 Q518 133 548 150 V230 H288Z" fill="#444b62"/>
    <path d="M288 181 Q330 154 377 180 Q453 148 548 173 V230 H288Z" fill="#313d50"/>
    {clouds}
    <!-- Stylized Pune fort: layered roofs, bastions and central gateway. -->
    <path d="M315 199 V166 H339 V145 H380 V163 H466 V145 H507 V166 H530 V199Z" fill="#584c58"/>
    <path d="M321 196 V170 H345 V149 H375 V168 H471 V149 H501 V170 H525 V196Z" fill="url(#stone)"/>
    <path d="M339 148 L360 134 L381 148Z M465 148 L486 134 L507 148Z" fill="#d5ad95"/>
    <path d="M339 148 H381 M465 148 H507 M375 168 H471" stroke="#493c50" stroke-width="3"/>
    <path d="M345 154 H375 M471 154 H501 M321 178 H397 M449 178 H525" stroke="#e2b69a" stroke-opacity=".5"/>
    <path d="M397 196 V167 L423 155 L449 167 V196Z" fill="#b88e7f"/>
    <path d="M394 167 L423 151 L452 167Z" fill="#dcb69a"/>
    <path d="M410 196 V179 Q423 159 436 179 V196Z" fill="#2b2c40"/>
    <path d="M415 196 V180 Q423 167 431 180 V196Z" fill="#554353"/>
    <path d="M423 174 V196 M415 184 H431" stroke="#b08770" stroke-width=".8"/>
    {windows}
    <path d="M360 135 V116" stroke="#d1af94" stroke-width="1.2"/>
    <path d="M361 116 l17 4 -17 7Z" fill="#e6a078"/>
    <path d="M288 200 Q358 185 402 197 L390 230 H288Z M444 197 Q487 187 548 201 V230 H461Z" fill="#253342"/>
    <path d="M410 197 H436 L463 230 H389Z" fill="#9e8c87" opacity=".5"/>
    <path d="M423 202 L423 226" stroke="#e1b89b" stroke-opacity=".3"/>
    <g fill="#1e2d3c"><path d="M302 230 V190 Q287 184 294 176 Q307 177 308 191 Q310 175 321 177 Q326 188 312 197 V230Z"/>
    <path d="M528 230 V188 Q513 177 518 167 Q532 167 534 185 Q535 175 546 176 Q551 189 538 196 V230Z"/></g>
    {effects}
    <rect x="288" y="12" width="260" height="218" rx="14" fill="none" stroke="#ffffff" stroke-opacity=".08"/>
    </g>'''


def render(now, current=None, stale=False):
    available = current is not None
    day = bool(current['is_day']) if available else None
    label, kind = describe(current['weather_code']) if available else ('Weather unavailable', 'unknown')
    accent = '#edc49c' if day else '#c3b9ed'
    period = ('Daytime' if day else 'Nighttime') if available else 'No weather data'
    temp = current['temperature_2m'] if available else None
    temperature = f'{temp:.0f}°' if available else '—'
    band = ('Cold' if temp < 15 else 'Cool' if temp < 22 else 'Mild' if temp < 28
            else 'Warm' if temp < 33 else 'Hot') if available else 'Unavailable'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="560" height="244" viewBox="0 0 560 244" role="img" aria-label="{escape('Pune weather: ' + temperature + ' Celsius, ' + label + ', ' + period + ', ' + now.strftime('%d %b %Y'))}">
<defs>
<linearGradient id="card" x2="1" y2="1"><stop stop-color="#202330"/><stop offset="1" stop-color="#121a27"/></linearGradient>
<clipPath id="scene"><rect x="288" y="12" width="260" height="218" rx="14"/></clipPath>
</defs>
<rect x=".5" y=".5" width="559" height="243" rx="22" fill="url(#card)" stroke="#3b3d4d"/>
{scene(day, kind)}
<g font-family="Arial,Helvetica,sans-serif">
<text x="26" y="31" font-size="9" letter-spacing="2.5" fill="{accent}">{'LAST KNOWN WEATHER' if stale else 'CURRENT WEATHER'}</text>
<text x="25" y="62" font-size="23" font-weight="600" fill="#f6eee7">Pune<tspan dx="7" font-size="12" font-weight="400" fill="#a2a4b5">/ India</tspan></text>
<text x="23" y="130" font-size="68" font-weight="500" letter-spacing="-4" fill="#f6eee7">{temperature}<tspan dx="8" font-size="23" letter-spacing="0" fill="#a5a7b8">C</tspan></text>
<text x="27" y="157" font-size="15" fill="#dedce5">{escape(label)}</text>
<circle cx="31" cy="178" r="3" fill="{accent}"/>
<text x="41" y="182" font-size="11" fill="{accent}">{period} · {band}</text>
<path d="M26 198 H257" stroke="#383b4b"/>
<text x="26" y="217" font-size="10" fill="#c1bfce">{now.strftime('%a, %d %b %Y')}</text>
<text x="26" y="232" font-size="8" fill="#9b9bad">{'Refresh delayed · Open-Meteo' if stale else 'Hourly snapshot · Open-Meteo'}</text>
</g></svg>'''



def validate(current):
    for key in ('temperature_2m', 'weather_code', 'is_day'):
        value = current.get(key)
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError('Invalid weather field: ' + key)
    if current['is_day'] not in (0, 1):
        raise ValueError('Invalid day/night reading')
    return current


def fetch_weather():
    # IPv4 avoids unreachable IPv6 routes on some hosted runners.
    # curl retries transient HTTP failures and connection errors.
    result = subprocess.run(
        ['curl', '--ipv4', '--fail', '--silent', '--show-error',
         '--connect-timeout', '10', '--max-time', '25',
         '--retry', '2', '--retry-delay', '2', '--retry-all-errors', URL],
        capture_output=True, text=True, timeout=90,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or 'Weather request failed')
    return validate(json.loads(result.stdout)['current'])


def main():
    stale = False
    try:
        current = fetch_weather()
        observed = datetime.fromisoformat(current['time']).replace(tzinfo=ZoneInfo('Asia/Kolkata'))
        snapshot = {'observed_at': observed.isoformat(), 'current': current}
        CACHE.parent.mkdir(exist_ok=True)
        CACHE.write_text(json.dumps(snapshot, indent=2) + '\n', encoding='utf-8')
        print('Fetched Pune weather:', current['temperature_2m'], 'C')
    except Exception as error:
        print('::warning::Weather refresh failed:', str(error))
        # A failed refresh must never destroy a valid card or invent a reading.
        if not CACHE.exists():
            raise RuntimeError('No saved reading; preserving existing widget') from error
        snapshot = json.loads(CACHE.read_text(encoding='utf-8'))
        current = validate(snapshot['current'])
        observed = datetime.fromisoformat(snapshot['observed_at'])
        stale = True
        print('Using saved reading from', observed.isoformat())
    svg = render(observed, current, stale=stale)
    (ROOT / 'assets').mkdir(exist_ok=True)
    (ROOT / 'assets/pune-dashboard.svg').write_text(
        '\n'.join(line.rstrip() for line in svg.splitlines()) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
