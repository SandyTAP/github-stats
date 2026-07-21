import os
import math
import requests

USERNAME = "SandyTAP"

headers = {}

token = os.getenv("GITHUB_TOKEN")
if token:
    headers["Authorization"] = f"Bearer {token}"

response = requests.get(
    f"https://api.github.com/users/{USERNAME}/repos?per_page=100",
    headers=headers
)

response.raise_for_status()

repos = response.json()

if not isinstance(repos, list):
    print(repos)
    raise SystemExit("GitHub API did not return a repository list.")

langs = {}

for repo in repos:
    if repo.get("fork"):
        continue

    data = requests.get(
        repo["languages_url"],
        headers=headers
    ).json()

    for lang, count in data.items():
        langs[lang] = langs.get(lang, 0) + count

langs = sorted(
    langs.items(),
    key=lambda x: x[1],
    reverse=True
)[:5]

total = sum(v for _, v in langs)

colors = [
    "#f1e05a",
    "#3572A5",
    "#89e051",
    "#e34c26",
    "#563d7c",
]

cx = 550
cy = 260
r = 140

start = 0
paths = []

for i, (lang, value) in enumerate(langs):
    pct = value / total
    angle = pct * 360

    end = start + angle

    x1 = cx + r * math.cos(math.radians(start - 90))
    y1 = cy + r * math.sin(math.radians(start - 90))

    x2 = cx + r * math.cos(math.radians(end - 90))
    y2 = cy + r * math.sin(math.radians(end - 90))

    large_arc = 1 if angle > 180 else 0

    paths.append(
        f'''
        <path d="
        M {x1} {y1}
        A {r} {r} 0 {large_arc} 1 {x2} {y2}
        "
        fill="none"
        stroke="{colors[i]}"
        stroke-width="56"
        />
        '''
    )

    start = end

legend = ""

for i, (lang, value) in enumerate(langs):
    percent = round(value / total * 100, 1)

    y = 120 + i * 55

    legend += f"""
    <rect x="90" y="{y-18}" width="24" height="24" fill="{colors[i]}"/>
    <text x="130" y="{y}" fill="#41d1c7" font-size="24">{lang} {percent}%</text>
    """

svg = f"""
<svg width="950" height="520"
xmlns="http://www.w3.org/2000/svg">

<rect
width="100%"
height="100%"
rx="12"
fill="#1a1b27"/>

<text
x="70"
y="70"
font-size="42"
fill="#70a5fd">
Top Languages
</text>

{legend}

{''.join(paths)}

<circle
cx="{cx}"
cy="{cy}"
r="90"
fill="#1a1b27"/>

</svg>
"""

with open("languages.svg", "w") as f:
    f.write(svg)
