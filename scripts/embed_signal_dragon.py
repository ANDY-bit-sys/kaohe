"""Embed the optimized model so snake.html also works from file://."""

import base64
import re
from pathlib import Path


root = Path(__file__).resolve().parents[1]
html_path = root / 'snake.html'
model_path = root / 'assets' / 'model' / 'signal-dragon-head.glb'
encoded = base64.b64encode(model_path.read_bytes()).decode('ascii')
html = html_path.read_text(encoding='utf-8')
pattern = r'(<script id="signal-dragon-model" type="application/octet-stream">).*?(</script>)'
updated, count = re.subn(pattern, lambda match: match.group(1) + encoded + match.group(2), html, flags=re.DOTALL)
if count != 1:
    raise RuntimeError(f'Expected one embedded-model slot, found {count}')
html_path.write_text(updated, encoding='utf-8')
print(f'Embedded {model_path.stat().st_size:,} bytes into {html_path.name} ({html_path.stat().st_size:,} bytes)')
