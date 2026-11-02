"""The Docket version is authoritative for UI builds and Clay publication."""
import re
import base64
import hashlib
from pathlib import Path

_docket = Path(__file__).resolve().parents[1] / 'desk/desk.docket-0'
_match = re.search(r'^\s*version\+\[(\d+) (\d+) (\d+)\]', _docket.read_text(), re.MULTILINE)
if not _match:
    raise ValueError('desk/desk.docket-0 must contain a three-part release version')
VERSION_PARTS = tuple(int(part) for part in _match.groups())
VERSION = '.'.join(map(str, VERSION_PARTS))

LOGO_SVG = (_docket.parents[1] / 'web/logo.svg').read_text()
FAVICON_URL = '/apps/ursketch/media/'+hashlib.sha256((_docket.parents[1]/'desk/media/images/pencil.svg').read_bytes()).hexdigest()[:16]+'/images/pencil.svg'
TILE_COLOR_HOON = re.search(r'^\s*color\+(0x[0-9a-f.]+)', _docket.read_text(), re.MULTILINE).group(1)
ICON_DATA_URL = 'data:image/png;base64,' + base64.b64encode((_docket.parents[1] / 'web/tile.png').read_bytes()).decode()
