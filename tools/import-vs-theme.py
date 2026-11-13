"""Decode a theme compiled into .pkgdef files back into .vstheme XML.

Used once to extract the built-in Visual Studio Light theme, the base of the light variants:
    python tools/import-vs-theme.py "C:/Program Files/Microsoft Visual Studio/18/Community/Common7/IDE" tools/base-light.xml

The first argument is a folder searched recursively for .pkgdef files, or a single .pkgdef file.
Options: --theme {GUID} (default: Light), --name NAME.

Compiled format of each "Data" value (little-endian):
    DWORD size, DWORD version (11), DWORD category count, then per category:
    GUID, DWORD color count, then per color:
    DWORD name length, name (ASCII), background, foreground
    where each of background and foreground is a type byte (0 = CT_INVALID: no value follows)
    followed by 4 bytes: R, G, B, A for CT_RAW, the little-endian DWORD Source otherwise.
"""
import argparse
import pathlib
import re
import struct
import uuid
from xml.sax.saxutils import escape

LIGHT = '{de3dbbcd-f642-433c-8353-8f1df4370aba}'
TYPES = ['CT_INVALID', 'CT_RAW', 'CT_COLORINDEX', 'CT_SYSCOLOR', 'CT_VSCOLOR', 'CT_AUTOMATIC',
         'CT_TRACK_FOREGROUND', 'CT_TRACK_BACKGROUND']
SECTION = re.compile(r'^\[\$RootKey\$\\Themes\\(\{[^}]+\})\\([^\]]+)\]\s*$', re.I | re.M)


def decode(data):
    """Yield (category GUID, [(name, background, foreground)]); colors are (type, source) or None."""
    pos = 12
    _size, version, count = struct.unpack_from('<III', data, 0)
    assert version == 11, version
    for _ in range(count):
        guid = '{' + str(uuid.UUID(bytes_le=bytes(data[pos:pos + 16]))) + '}'
        pos += 16
        (colors,) = struct.unpack_from('<I', data, pos)
        pos += 4
        items = []
        for _ in range(colors):
            (length,) = struct.unpack_from('<I', data, pos)
            pos += 4
            name = bytes(data[pos:pos + length]).decode('ascii')
            pos += length
            slots = []
            for _ in range(2):
                kind = data[pos]
                pos += 1
                if kind == 0:
                    slots.append(None)
                    continue
                b0, b1, b2, b3 = data[pos:pos + 4]
                pos += 4
                source = f'{b3:02X}{b0:02X}{b1:02X}{b2:02X}' if kind == 1 else f'{b3:02X}{b2:02X}{b1:02X}{b0:02X}'
                slots.append((TYPES[kind], source))
            items.append((name, slots[0], slots[1]))
        yield guid, items


def sections(text):
    """Yield (theme GUID, category name, data bytes) for each theme category of a .pkgdef."""
    matches = list(SECTION.finditer(text))
    for i, m in enumerate(matches):
        body = text[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(text)]
        data = re.search(r'"Data"\s*=\s*hex:((?:[0-9a-fA-F]{2}|[,\s\\])+)', body)
        if data:
            yield m.group(1).lower(), m.group(2), bytes.fromhex(re.sub(r'[^0-9a-fA-F]', '', data.group(1)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('output')
    parser.add_argument('--theme', default=LIGHT)
    parser.add_argument('--name', default='Light')
    args = parser.parse_args()

    source = pathlib.Path(args.source)
    files = [source] if source.is_file() else sorted(source.rglob('*.pkgdef'))
    theme = args.theme.lower()
    categories = {}  # GUID -> (name, {color name: (background, foreground)})
    for path in files:
        try:
            text = path.read_text(encoding='utf-8-sig', errors='replace')
        except OSError:
            continue
        if theme not in text.lower():
            continue
        for guid, category, data in sections(text):
            if guid != theme:
                continue
            for cat_guid, items in decode(data):
                _, colors = categories.setdefault(cat_guid, (category, {}))
                for name, background, foreground in items:
                    colors[name] = (background, foreground)

    lines = ['<Themes>', f'  <Theme Name="{escape(args.name)}" GUID="{theme}">']
    for cat_guid, (category, colors) in sorted(categories.items(), key=lambda c: c[1][0].lower()):
        lines.append(f'    <Category Name="{escape(category)}" GUID="{cat_guid}">')
        for name, (background, foreground) in colors.items():
            lines.append(f'      <Color Name="{escape(name, {chr(34): "&quot;"})}">')
            for slot, value in (('Background', background), ('Foreground', foreground)):
                if value:
                    lines.append(f'        <{slot} Type="{value[0]}" Source="{value[1]}" />')
            lines.append('      </Color>')
        lines.append('    </Category>')
    lines += ['  </Theme>', '</Themes>', '']
    pathlib.Path(args.output).write_text('\n'.join(lines), encoding='utf-8-sig', newline='\r\n')
    print(f'{args.output}: {len(categories)} categories, {sum(len(c) for _, c in categories.values())} colors')


if __name__ == '__main__':
    main()
