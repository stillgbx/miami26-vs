"""Render bin/preview.html: a mock-up of Visual Studio in each generated theme, to compare them at a glance.

Every color is read from the .vstheme files and the glow from Glow/GlowPalette.cs, so the page shows
what the themes contain. It is only a sketch of the IDE: check the real thing in Visual Studio.
    python tools/preview-themes.py
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'bin' / 'preview.html'
GLOW_BRIGHTNESS = 0.6  # default of the Brightness option

ENVIRONMENT = '{624ed9c3-bdfd-41fa-96c3-7c824ea32e3d}'
TEXT_MANAGER = '{58e96763-1d3b-4e05-b6ba-ff7115fd0b7b}'
MEF_ITEMS = '{75a05685-00a8-4ded-bae5-e7a50bfa929a}'
TREE_VIEW = '{92ecf08e-8b13-4cf4-99e9-ae2692382185}'
SHELL_INTERNAL = '{5af241b7-5627-4d12-bfb1-2b67d11127d7}'  # Visual Studio 2026 frame

# (token role, text) lines of the sample, None for plain text
SAMPLE = [
    [('comment', '// Cruising down the ocean front after sunset.')],
    [('keyword', 'public sealed class '), ('type', 'OceanDrive'), (None, ' : '), ('type', 'IStrip')],
    [(None, '{')],
    [(None, '    '), ('keyword', 'private const int '), ('variable', 'MaxCruisers'), ('operator', ' = '), ('constant', '8'), (None, ';')],
    [(None, '    '), ('keyword', 'private readonly '), ('type', 'List'), (None, '<'), ('type', 'Ride'), (None, '> '),
     ('variable', 'cruisers'), ('operator', ' = '), ('keyword', 'new'), (None, '();')],
    [],
    [(None, '    '), ('keyword', 'public bool '), ('function', 'Cruise'), (None, '('), ('type', 'Ride'), (None, ' '),
     ('variable', 'ride'), (None, ')')],
    [(None, '    {')],
    [(None, '        '), ('keyword', 'if '), (None, '('), ('variable', 'ride'), ('operator', ' == '), ('keyword', 'null'),
     ('operator', ' || '), ('variable', 'cruisers'), (None, '.'), ('variable', 'Count'), ('operator', ' >= '),
     ('variable', 'MaxCruisers'), (None, ')')],
    [(None, '            '), ('keyword', 'return '), ('keyword', 'false'), (None, ';')],
    [],
    [(None, '        '), ('variable', 'cruisers'), (None, '.'), ('function', 'Add'), (None, '('), ('variable', 'ride'), (None, ');')],
    [(None, '        '), ('type', 'Console'), (None, '.'), ('function', 'WriteLine'), (None, '('), ('string', '$"Friday '),
     ('escape', '\\"'), ('string', 'neon'), ('escape', '\\"'), ('string', ' night: {'), ('variable', 'ride'), ('string', '}"'), (None, ');')],
    [(None, '        '), ('keyword', 'return '), ('keyword', 'true'), (None, ';')],
    [(None, '    }')],
    [(None, '}')],
]

TOKEN_NAMES = {'keyword': 'Keyword', 'type': 'class name', 'function': 'method name', 'variable': 'local name',
               'operator': 'Operator', 'string': 'String', 'constant': 'Number', 'comment': 'Comment',
               'escape': 'string - escape character'}


def load(path):
    """{(category GUID, color name): {'Background': '#RRGGBB', 'Foreground': ...}} of the CT_RAW colors."""
    text = path.read_text(encoding='utf-8-sig')
    colors = {}
    for cm in re.finditer(r'<Category Name="[^"]*" GUID="(\{[^}]+\})">(.*?)</Category>', text, re.S):
        for c in re.finditer(r'<Color Name="([^"]*)">(.*?)</Color>', cm.group(2), re.S):
            slots = colors.setdefault((cm.group(1).lower(), html.unescape(c.group(1))), {})
            for s in re.finditer(r'<(Background|Foreground) Type="CT_RAW" Source="([0-9A-F]{2})([0-9A-F]{6})"', c.group(2)):
                slots[s.group(1)] = '#' + s.group(3) + ('' if s.group(2) == 'FF' else s.group(2))
    name = re.search(r'<Theme Name="([^"]*)"', text).group(1)
    return html.unescape(name), colors, 'Name="NeonGlow"' in text


def glow_shadows():
    shadows = {}
    source = (ROOT / 'Glow' / 'GlowPalette.cs').read_text(encoding='utf-8')
    for m in re.finditer(r'\[Rgb\(0x([0-9A-Fa-f]{6})\)\] = new\[\] \{(.*?)\}', source):
        layers = []
        for kind, args in re.findall(r'(Dark|Neon|Fixed)\(([^)]*)\)', m.group(2)):
            parts = [p.strip() for p in args.split(',')]
            blur, rgb = float(parts[0]), parts[-1][2:]
            r, g, b = (int(rgb[i:i + 2], 16) for i in (0, 2, 4))
            alpha = {'Dark': 1, 'Neon': GLOW_BRIGHTNESS}.get(kind) or int(parts[1], 16) / 255
            layers.append(f'0 0 {blur:g}px rgba({r},{g},{b},{alpha:.2f})')
        shadows['#' + m.group(1).upper()] = ', '.join(layers)
    return shadows


def render(path, shadows):
    name, colors, glow = load(path)

    def get(category, color, slot='Background', default='#FF00FF'):
        return colors.get((category, color), {}).get(slot, default)

    env = lambda color, default='#FF00FF': get(ENVIRONMENT, color, default=default)
    editor_bg = get(TEXT_MANAGER, 'Plain Text')
    text = get(TEXT_MANAGER, 'Plain Text', 'Foreground')

    def token(role):
        return get(MEF_ITEMS, TOKEN_NAMES[role], 'Foreground', text)

    lines = []
    for number, line in enumerate(SAMPLE, 1):
        spans = []
        for role, content in line:
            color = token(role) if role else text
            style = f'color:{color}'
            if glow and color.upper() in shadows:
                style += f';text-shadow:{shadows[color.upper()]}'
            spans.append(f'<span style="{style}">{html.escape(content)}</span>')
        current = number == 9
        line_style = f' style="box-shadow:inset 0 0 0 1px {get(MEF_ITEMS, "CurrentLineActiveFormat", "Foreground", editor_bg)}"' if current else ''
        selection = get(TEXT_MANAGER, 'Selected Text')
        body = ''.join(spans)
        if number == 12:
            first, rest = body.split('</span>', 1)
            body = first + '</span>' + rest.replace('<span style="', f'<span style="background:{selection};', 4)
        lines.append(f'<div class="line"{line_style}><span class="ln" style="color:{get(MEF_ITEMS, "Line Number", "Foreground")}">{number}</span>{body}</div>')

    tree = ''
    for depth, label, selected in [(0, 'Solution "Miami26"', False), (1, 'Examples', False), (2, 'OceanDrive.cs', True),
                                   (2, 'Ride.cs', False), (1, 'Glow', False), (1, 'README.md', False)]:
        style = f'padding-left:{8 + depth * 14}px'
        if selected:
            style += f';background:{get(TREE_VIEW, "SelectedItemActive", default=env("Highlight", "#888"))}' \
                     f';color:{get(TREE_VIEW, "SelectedItemActive", "Foreground", "#FFF")}'
        tree += f'<div style="{style}">{html.escape(label)}</div>'

    # Visual Studio 2026 colors first, then the earlier ones
    shell = lambda color, fallback: get(SHELL_INTERNAL, color, default=fallback)
    frame = shell('EnvironmentBackground', env('EnvironmentBackground'))
    panel = shell('EnvironmentTab', env('ToolWindowBackground'))
    status_bg = shell('StatusBarBackgroundFillRest', env('StatusBarDefault'))
    status_fg = shell('StatusBarTextFillRest', get(ENVIRONMENT, 'StatusBarDefault', 'Foreground', '#FFF'))
    return f'''
<section>
  <h2>{html.escape(name)}{' <small>neon glow</small>' if glow else ''}</h2>
  <div class="ide" style="background:{frame};color:{env('CommandBarTextActive')}">
    <div class="title" style="background:{frame};color:{env('CommandBarTextActive', '#888')}">
      <span>File&nbsp;&nbsp;Edit&nbsp;&nbsp;View&nbsp;&nbsp;Git&nbsp;&nbsp;Project&nbsp;&nbsp;Build&nbsp;&nbsp;Debug</span>
      <span class="search" style="background:{get('{f1095fad-881f-45f1-8580-589e10325eb8}', 'Unfocused', default=env('ComboBoxBackground'))};border-color:{get('{f1095fad-881f-45f1-8580-589e10325eb8}', 'UnfocusedBorder', default=env('ComboBoxBorder'))};color:{get('{f1095fad-881f-45f1-8580-589e10325eb8}', 'UnfocusedWatermarkText', default='#888')}">Search</span>
    </div>
    <div class="body">
      <div class="doc">
        <div class="tabs" style="background:{frame}">
          <span class="tab" style="background:{env('FileTabSelectedBackground')};color:{env('FileTabSelectedText')}">OceanDrive.cs</span>
          <span class="tab" style="background:{env('FileTabInactiveGradientTop', env('FileTabBackground', 'transparent'))};color:{env('FileTabInactiveText', env('FileTabText'))}">Ride.cs</span>
          <span class="tab" style="color:{env('FileTabText')}">README.md</span>
        </div>
        <div class="editor" style="background:{editor_bg};color:{text}">{''.join(lines)}</div>
      </div>
      <div class="tool" style="background:{panel};color:{env('ToolWindowText')};border-color:{env('ToolWindowBorder', 'transparent')}">
        <div class="tooltitle" style="background:{panel};color:{env('ToolWindowTabSelectedActiveText', env('ToolWindowText'))}">Solution Explorer</div>
        {tree}
      </div>
    </div>
    <div class="status" style="background:{status_bg};color:{status_fg}">Ready&nbsp;&nbsp;&nbsp;Ln 12, Col 9&nbsp;&nbsp;&nbsp;main</div>
  </div>
</section>'''


def main():
    shadows = glow_shadows()
    themes = sorted(ROOT.glob('*.vstheme'))
    page = f'''<!doctype html>
<html><head><meta charset="utf-8"><title>Miami '26 preview</title>
<style>
  body {{ background:#222; color:#eee; font:14px Segoe UI, sans-serif; margin:24px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(640px, 1fr)); gap:24px; }}
  h2 {{ font-weight:600; margin:0 0 8px; }} small {{ font-weight:400; opacity:.6; }}
  .ide {{ border-radius:6px; overflow:hidden; font-size:12px; }}
  .title {{ display:flex; justify-content:space-between; align-items:center; padding:6px 10px; }}
  .search {{ border:1px solid; border-radius:4px; padding:2px 40px 2px 8px; opacity:.85; }}
  .body {{ display:flex; }} .doc {{ flex:1; min-width:0; }}
  .tabs {{ display:flex; }} .tab {{ padding:5px 14px; }}
  .editor {{ font:13px Cascadia Code, Consolas, monospace; padding:8px 0; white-space:pre; overflow:hidden; }}
  .line {{ height:19px; line-height:19px; }} .ln {{ display:inline-block; width:34px; text-align:right; margin-right:14px; }}
  .tool {{ width:190px; border-left:1px solid; line-height:22px; }}
  .tooltitle {{ padding:3px 8px; font-weight:600; }}
  .status {{ padding:3px 10px; }}
</style></head>
<body><div class="grid">{''.join(render(t, shadows) for t in themes)}</div></body></html>
'''
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(page, encoding='utf-8')
    print(f'{OUTPUT.relative_to(ROOT)} generated')


if __name__ == '__main__':
    main()
