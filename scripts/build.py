#!/usr/bin/env python3
"""Embed the dependency-free browser client in a Hoon cord."""
from pathlib import Path
import base64
import json
import re
from media_assets import media_assets, write_media
from release import VERSION, LOGO_SVG, ICON_DATA_URL, FAVICON_URL

ROOT = Path(__file__).resolve().parents[1]
(ROOT/'desk/media/images/app-tile.png').write_bytes((ROOT/'web/tile.png').read_bytes())
assets = media_assets()
write_media(assets)
html = (ROOT / 'web/index.html').read_text().replace('URSKETCH_APP_VERSION', VERSION).replace('<!-- URSKETCH_LOGO -->', LOGO_SVG).replace('URSKETCH_FAVICON_URL', FAVICON_URL)
docket = ROOT / 'desk/desk.docket-0'
lines = [line for line in docket.read_text().splitlines() if not line.strip().startswith('image+')]
lines.insert(next(i for i,line in enumerate(lines) if line.strip().startswith('version+')), "  image+'"+ICON_DATA_URL+"'")
docket.write_text('\n'.join(lines)+'\n')
html = html.replace('<!-- URSKETCH_CONNECT_LOGO -->', (ROOT/'web/connect-logo.svg').read_text().replace('<svg ', '<svg id="connect-logo" ', 1).replace('URSKETCH_CONNECT_LOGO_IMAGE', assets['images/ursketch-logo.png']['url']))
html = html.replace('URSKETCH_BROWSER_LOGO_URL', assets['images/ursketch-logo.png']['url'])
classic = (ROOT / 'web/classic.css').read_text()
for name in ('tools', 'hint', 'done'):
    uri = 'data:image/gif;base64,' + base64.b64encode((ROOT / f'web/classic-assets/{name}.gif').read_bytes()).decode()
    classic = classic.replace(f'CLASSIC_{name.upper()}_IMAGE', uri)
for name in ('metal', 'metal-small'):
    uri = 'data:image/svg+xml;base64,' + base64.b64encode((ROOT / f'web/classic-assets/{name}.svg').read_bytes()).decode()
    classic = classic.replace('CLASSIC_'+name.upper().replace('-', '_')+'_IMAGE', uri)
theme_css=(ROOT/'web/theme-art.css').read_text()+'\n'+(ROOT/'web/themes.css').read_text()
for path in sorted((ROOT/'web/theme-art').glob('*.svg')):
    theme_css=theme_css.replace('THEME_ART_'+path.stem.upper().replace('-','_'),'data:image/svg+xml;base64,'+base64.b64encode(path.read_bytes()).decode())
html = html.replace('/* URSKETCH_CSS */', (ROOT / 'web/style.css').read_text().replace('/* URSKETCH_CLASSIC */', classic).replace('/* URSKETCH_CONNECT */', (ROOT/'web/connect.css').read_text()).replace('/* URSKETCH_BROWSER */', (ROOT/'web/browser.css').read_text()).replace('/* URSKETCH_BLINGEE */', (ROOT/'web/blingee.css').read_text()).replace('/* URSKETCH_THEMES */',theme_css))
html=html.replace('</style>',(ROOT/'web/settings-layout.css').read_text()+'</style>',1)
for name in ('skip', 'done'):
    uri = 'data:image/svg+xml;base64,' + base64.b64encode((ROOT / f'web/hint-{name}.svg').read_bytes()).decode()
    html = html.replace(f'DEFAULT_HINT_{name.upper()}_IMAGE', uri)
html = html.replace('<script>/* URSKETCH_DRAWING */', '<script>window.URSKETCH_SHIP=URSKETCH_SHIP_VALUE;/* URSKETCH_DRAWING */', 1)
characters=json.loads((ROOT/'web/characters.json').read_text())
for entries in characters['parts'].values():
    for entry in entries:
        if entry.get('asset'):entry['url']=assets[entry['asset']]['url']
html=html.replace('/* URSKETCH_CHARACTERS */',(ROOT/'web/characters.js').read_text().replace('URSKETCH_CHARACTER_CATALOG',json.dumps(characters,separators=(',',':'))))
html = html.replace('/* URSKETCH_DRAWING */', (ROOT / 'web/drawing.js').read_text())
html = html.replace('/* URSKETCH_SETTINGS */', (ROOT / 'web/settings.js').read_text())
cue_urls = {Path(name).stem:asset['url'] for name,asset in assets.items() if name.startswith('audio/cues/')}
html = html.replace('/* URSKETCH_FINALE */', (ROOT/'web/finale.js').read_text())
html = html.replace('/* URSKETCH_AUDIO */', (ROOT/'web/audio.js').read_text())
chat_host=json.loads((ROOT/'web/chat-config.json').read_text())['host']
if not re.fullmatch(r'~[a-z-]+',chat_host): raise ValueError('Invalid Global Chat host')
html = html.replace('/* URSKETCH_JS */', (ROOT / 'web/app.js').read_text().replace('URSKETCH_PENCIL_URL',assets['images/pencil.svg']['url']).replace('URSKETCH_GLOBAL_CHAT_HOST', json.dumps(chat_host)).replace('URSKETCH_CUE_URLS', json.dumps(cue_urls)))
before, after = html.split('URSKETCH_SHIP_VALUE', 1)
intro = (ROOT/'web/intro.html').read_text().replace('URSKETCH_FAVICON_URL', FAVICON_URL)
settings_dialog = re.search(r'<dialog id="settings-dialog".*?</dialog>', html, re.DOTALL).group()
intro = intro.replace('<!-- URSKETCH_SETTINGS_DIALOG -->', settings_dialog).replace('/* URSKETCH_SETTINGS */', (ROOT/'web/settings.js').read_text())
intro = intro.replace('/* URSKETCH_INTRO_CSS */', (ROOT/'web/intro.css').read_text()+'\n'+(ROOT/'web/settings-layout.css').read_text())
intro = intro.replace('/* URSKETCH_INTRO_JS */', (ROOT/'web/intro.js').read_text())
intro = intro.replace('URSKETCH_INTRO_MOTION', (ROOT/'web/intro-motion.json').read_text().strip())
for marker,name in [('VIDEO','video/intro.mp4'),('AUDIO','audio/music/theme_song.mp3'),('POSTER','images/intro-poster.jpg'),('MASK','images/intro-wordmark-mask.png'),('WORDMARK','images/ursketch-logo.png')]:
    intro = intro.replace('URSKETCH_INTRO_'+marker+'_URL', assets[name]['url'])
(ROOT/'artifacts/media-manifest.json').write_text(json.dumps({k:{field:value for field,value in v.items() if field!='data'} for k,v in assets.items()},indent=2)+'\n')

def cord(text):
    return "'" + ''.join('\\%02x' % b if b in (10,13,39,92) or b < 32 or b > 126 else chr(b) for b in text.encode()) + "'"

result = "::  Generated by scripts/build.py; edit web/ sources.\n|%\n++  index\n  |=  who=@p\n  ^-  @t\n  (cat 3 " + cord(before) + " (cat 3 (cat 3 '\\27' (cat 3 (scot %p who) '\\27')) " + cord(after) + "))\n++  intro\n  ^-  @t\n  " + cord(intro) + "\n--\n"
(ROOT / 'desk/lib/ursketch-assets.hoon').write_text(result)
print(f'Embedded {len(html.encode()):,} bytes → desk/lib/ursketch-assets.hoon')
