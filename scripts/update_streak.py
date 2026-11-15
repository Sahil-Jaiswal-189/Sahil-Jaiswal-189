"""Save the streak card locally to avoid GitHub Camo's day-long external-image cache."""
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
URL = ('https://streak-stats.demolab.com/?user=Sahil-Jaiswal-189'
       '&theme=tokyonight&hide_border=true')


def save_card(svg):
    root = ET.fromstring(svg)
    labels = ' '.join(root.itertext())
    if root.tag != '{http://www.w3.org/2000/svg}svg' or not all(
        label in labels for label in ('Total Contributions', 'Current Streak', 'Longest Streak')
    ):
        raise ValueError('Streak service returned an error card; keeping the previous image')
    output = ROOT / 'assets/github-streak.svg'
    output.parent.mkdir(exist_ok=True)
    output.write_bytes(svg)


def main():
    request = Request(URL, headers={'User-Agent': 'Sahil-profile-widget', 'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=30) as response:
        svg = response.read()
    save_card(svg)
    print('Updated local contribution streak card')


if __name__ == '__main__':
    main()
