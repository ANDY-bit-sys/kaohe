"""Prepare the Hunyuan GLB for the offline, single-file snake game.

The original 4K PBR maps stay in output/hunyuan. The website uses only the
base-color map at game size, so the published GLB keeps its mesh and a 2K JPEG.
"""

import io
import json
import struct
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = next((ROOT / 'output' / 'hunyuan').glob('*.glb'))
TARGET = ROOT / 'assets' / 'model' / 'signal-dragon-head.glb'


def pad(data: bytes, byte: bytes) -> bytes:
    return data + byte * ((-len(data)) % 4)


raw = SOURCE.read_bytes()
assert raw[:4] == b'glTF' and struct.unpack_from('<I', raw, 4)[0] == 2
json_len = struct.unpack_from('<I', raw, 12)[0]
gltf = json.loads(raw[20:20 + json_len])
bin_start = 20 + json_len
assert raw[bin_start + 4:bin_start + 8] == b'BIN\0'
binary = raw[bin_start + 8:]

primitive = gltf['meshes'][0]['primitives'][0]
assert len(gltf['meshes']) == 1 and len(gltf['images']) == 3
assert primitive['attributes'].keys() == {'POSITION', 'NORMAL', 'TEXCOORD_0'}
geometry_end = max(view['byteOffset'] + view['byteLength'] for view in gltf['bufferViews'][:4])
packed = bytearray(binary[:geometry_end])

color_image = gltf['images'][1]
color_view = gltf['bufferViews'][color_image['bufferView']]
color_bytes = binary[color_view['byteOffset']:color_view['byteOffset'] + color_view['byteLength']]
with Image.open(io.BytesIO(color_bytes)) as image:
    assert image.mode == 'RGB'
    image.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=90, subsampling=0, optimize=True)
    color_bytes = output.getvalue()

packed.extend(b'\0' * ((-len(packed)) % 4))
image_offset = len(packed)
packed.extend(color_bytes)

gltf['bufferViews'] = gltf['bufferViews'][:4] + [{
    'buffer': 0,
    'byteOffset': image_offset,
    'byteLength': len(color_bytes),
}]
gltf['images'] = [{'bufferView': 4, 'mimeType': 'image/jpeg', 'name': 'signal-dragon-base-color'}]
gltf['textures'] = [{'sampler': 0, 'source': 0}]
material = gltf['materials'][0]
material.pop('normalTexture', None)
material.pop('extensions', None)
material['pbrMetallicRoughness'] = {
    'baseColorTexture': {'index': 0},
    'metallicFactor': 0.35,
    'roughnessFactor': 0.45,
}
gltf.pop('extensionsUsed', None)
gltf['buffers'][0]['byteLength'] = len(packed)

json_chunk = pad(json.dumps(gltf, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), b' ')
bin_chunk = pad(bytes(packed), b'\0')
file_length = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_bytes(
    struct.pack('<4sII', b'glTF', 2, file_length)
    + struct.pack('<I4s', len(json_chunk), b'JSON') + json_chunk
    + struct.pack('<I4s', len(bin_chunk), b'BIN\0') + bin_chunk
)
print(f'{TARGET.relative_to(ROOT)}: {file_length:,} bytes (source {len(raw):,} bytes)')
