"""Generate the four Miami '26 themes: two palettes, each in a dark and a light version.

* Bay: a day on the bay. Sky blue, turquoise water, lavender palm trees, peach facades, warm sand.
* Sunset: dusk on the ocean front. Magenta, peach, pale gold, periwinkle and lavender sky, plum palm trees.

The dark versions are built on tools/base-dark.xml, the environment of SynthWave '84
(github.com/stillgbx/synthwave-vs). The light versions are built on tools/base-light.xml, the
built-in Visual Studio Light theme, extracted with tools/import-vs-theme.py. Both bases are not
named *.vstheme on purpose: VsixColorCompiler would compile them and ship them as extra themes.

How the colors are set:
* DARK_ROLES and LIGHT_ROLES name the main colors of each base (backgrounds, accent, text...).
  Each palette gives its own color for every role.
* The other colors of a base are adapted by adapt(): blues move to the accent of the palette and
  purples to its tertiary color. Greys take the hue of the palette in the dark themes; in the light
  ones they follow its 'ramp', which turns the whites of Visual Studio Light into pastels.
* EDITOR sets the text editor colors (background, selection, caret...) and 'tokens' the syntax colors.

Edit the palettes below, then run
    python tools/generate-themes.py
It writes the four .vstheme files at the root of the repository.
"""
import colorsys
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DARK_BASE = ROOT / 'tools' / 'base-dark.xml'
LIGHT_BASE = ROOT / 'tools' / 'base-light.xml'
GLOW_PALETTE = ROOT / 'Glow' / 'GlowPalette.cs'

DARK_FALLBACK = '{1ded0138-47ce-435e-84ef-9ec1f439b749}'
LIGHT_FALLBACK = '{de3dbbcd-f642-433c-8353-8f1df4370aba}'

# Main colors of the SynthWave '84 environment -> role
DARK_ROLES = {
    '170926': 'bg0',          # menus, popups
    '1E122A': 'bg1',          # editor, tool windows
    '241B2F': 'bg2',          # environment, title bar
    '2A2139': 'bg3',          # borders, inactive tabs, controls
    '463465': 'menu',
    '3D3651': 'thumb',        # scroll bar thumb
    '53406A': 'raised',       # tooltips, separators
    '442359': 'pressed',
    '534A5E': 'muted',
    '574F66': 'muted',
    '8A8592': 'dim',          # line numbers
    'F1F1F1': 'text',
    '23A9F2': 'accent',
    '3399FF': 'selection',
    '55AAFF': 'accent_hover',
    '4CBCF6': 'accent_hot',
    '74CEFB': 'accent_soft',
    '9DE1FF': 'heading',
    '0F7093': 'secondary',    # last active tab, building status bar
    '6EBBDB': 'secondary_light',
    '3E96B7': 'secondary_mid',
    '004B8E': 'secondary_dark',
    '68217A': 'tertiary',     # provisional tab, no solution status bar
    '8631C7': 'tertiary_light',
    'F97E72': 'warm',         # debugging status bar
}

# Main colors of the Visual Studio Light theme -> role. Its whites and greys are not listed: they follow
# the 'ramp' of the palette (see adapt()), so that the light themes are pastel instead of white.
LIGHT_ROLES = {
    '5649B0': 'accent',       # the Visual Studio 2026 accent
    '3F3682': 'accent_dark',
    '221D46': 'accent_darker',
    '006CBE': 'accent',
    '007ACC': 'accent',
    '0078D4': 'accent',
    '0E70C0': 'accent_dark',
    '005BA1': 'accent_dark',
    '0E6198': 'accent_darker',
    '0E639C': 'accent_darker',
    '1C97EA': 'accent_hover',
    '52B0EF': 'accent_soft',
    '3399FF': 'selection',
    'C9DEF5': 'accent_pale',  # hovered and selected items
    'F3F9FF': 'accent_wash',
    '2B91AF': 'secondary',
    '68217A': 'tertiary',
    '865FC5': 'tertiary_light',
}

# Text editor categories
TEXT_MANAGER = '{58e96763-1d3b-4e05-b6ba-ff7115fd0b7b}'
MEF_ITEMS = '{75a05685-00a8-4ded-bae5-e7a50bfa929a}'
LANGUAGE_SERVICE_ITEMS = '{e0187991-b458-4f7e-8ca9-42c9a573b56c}'
TEXT_MARKER = '{ff349800-ea43-46c1-8c98-878e78f46501}'
ENVIRONMENT = '{624ed9c3-bdfd-41fa-96c3-7c824ea32e3d}'
SHELL_INTERNAL = '{5af241b7-5627-4d12-bfb1-2b67d11127d7}'  # Visual Studio 2026 frame
CATEGORY_NAMES = {
    TEXT_MANAGER: 'Text Editor Text Manager Items',
    MEF_ITEMS: 'Text Editor MEF Items',
    TEXT_MARKER: 'Text Editor Text Marker Items',
}

# Named colors set from the palette: (category, color name) -> (background role, foreground role)
EDITOR = {
    (TEXT_MANAGER, 'Plain Text'): ('editor', 'text'),
    (TEXT_MANAGER, 'Selected Text'): ('editor_selection', None),
    (TEXT_MANAGER, 'Inactive Selected Text'): ('editor_inactive_selection', None),
    (TEXT_MANAGER, 'Indicator Margin'): ('editor', None),
    (MEF_ITEMS, 'Selected Text'): ('editor_selection', None),
    (MEF_ITEMS, 'Inactive Selected Text'): ('editor_inactive_selection', None),
    (MEF_ITEMS, 'Line Number'): (None, 'line_number'),
    (MEF_ITEMS, 'Caret (Primary)'): (None, 'caret'),
    (MEF_ITEMS, 'Caret (Secondary)'): (None, 'caret_secondary'),
    (MEF_ITEMS, 'CurrentLineActiveFormat'): (None, 'current_line'),
    (MEF_ITEMS, 'MarkerFormatDefinition/HighlightedReference'): ('highlight', None),
    (TEXT_MARKER, 'Brace Matching (Rectangle)'): ('highlight', None),
    (ENVIRONMENT, 'StatusBarDefault'): ('status', 'status_text'),
    (ENVIRONMENT, 'StatusBarDebugging'): ('warm', 'status_dark_text'),
    (ENVIRONMENT, 'StatusBarBuilding'): ('secondary', 'status_text'),
    # Visual Studio 2026 status bar
    (SHELL_INTERNAL, 'StatusBarBackgroundFillRest'): ('status', None),
    (SHELL_INTERNAL, 'StatusBarTextFillRest'): ('status_text', None),
    (SHELL_INTERNAL, 'StatusBarBackgroundFillBuilding'): ('secondary', None),
    (SHELL_INTERNAL, 'StatusBarTextFillBuilding'): ('status_text', None),
    (SHELL_INTERNAL, 'StatusBarBackgroundFillDebugging'): ('warm', None),
    (SHELL_INTERNAL, 'StatusBarTextFillDebugging'): ('status_dark_text', None),
    (SHELL_INTERNAL, 'StatusBarBackgroundFillSolutionLoading'): ('tertiary', None),
    (SHELL_INTERNAL, 'StatusBarTextFillSolutionLoading'): ('status_text', None),
}

TOKEN_ROLES = {
    'keyword': [
        'Keyword', 'keyword - control',
        'CppControlKeywordSyntacticTokenFormat', 'CppNewDeleteSemanticTokenFormat', 'C/C++ User Keywords',
        'CSS Keyword',
    ],
    'operator': [
        'Operator', 'operator - overloaded', 'CppOperatorSemanticTokenFormat', 'CppMemberOperatorSemanticTokenFormat',
    ],
    'attribute': [
        'HTML Attribute Name', 'HTML Attribute', 'Markup Attribute', 'XML Attribute', 'XAML Attribute',
    ],
    'string': [
        'String', 'string - verbatim', 'CSS String Value', 'VBScript String', 'CppStringDelimiterCharacterSyntacticTokenFormat',
        'HTML Attribute Value', 'Markup Attribute Value', 'XML Attribute Value', 'XAML Attribute Value',
        'XML Attribute Quotes', 'XAML Attribute Quotes',
    ],
    'constant': [
        'Number', 'VBScript Number', 'CppUDLNumberSemanticTokenFormat', 'constant name', 'enum member name',
        'CSS Property Value',
    ],
    'comment': [
        'Comment', 'CSS Comment', 'HTML Comment', 'VBScript Comment', 'XAML Comment', 'XML Comment',
        'XML Doc Comment', 'XML Doc Tag', 'regex - comment',
        'xml doc comment - attribute name', 'xml doc comment - attribute quotes', 'xml doc comment - attribute value',
        'xml doc comment - cdata section', 'xml doc comment - comment', 'xml doc comment - delimiter',
        'xml doc comment - entity reference', 'xml doc comment - name', 'xml doc comment - processing instruction',
        'xml doc comment - text',
    ],
    'type': [
        'Type', 'class name', 'record class name', 'struct name', 'record struct name', 'interface name', 'enum name',
        'delegate name', 'module name', 'type parameter name', 'namespace name',
        'CppTypeSemanticTokenFormat', 'CppClassTemplateSemanticTokenFormat', 'CppGenericTypeSemanticTokenFormat',
        'CppRefTypeSemanticTokenFormat', 'CppValueTypeSemanticTokenFormat', 'CppEnumSemanticTokenFormat',
        'CppNamespaceSemanticTokenFormat',
    ],
    'function': [
        'method name', 'extension method name',
        'CppFunctionSemanticTokenFormat', 'CppFunctionTemplateSemanticTokenFormat',
        'CppMemberFunctionSemanticTokenFormat', 'CppStaticMemberFunctionSemanticTokenFormat',
    ],
    'escape': [
        'string - escape character', 'CppStringEscapeCharacterSyntacticTokenFormat',
        'HTML Tag Delimiter', 'XML Delimiter', 'XAML Delimiter', 'xml literal - delimiter',
    ],
    'variable': [
        'Identifier', 'local name', 'parameter name', 'field name', 'property name', 'event name',
        'CppLocalVariableSemanticTokenFormat', 'CppParameterSemanticTokenFormat', 'CppMemberFieldSemanticTokenFormat',
        'CppGlobalVariableSemanticTokenFormat', 'CppStaticMemberFieldSemanticTokenFormat',
        'CppPropertySemanticTokenFormat', 'CppEventSemanticTokenFormat',
    ],
    'tag': [
        'Preprocessor Keyword', 'CppMacroSemanticTokenFormat',
        'HTML Element Name', 'Markup Node', 'XML Name', 'XAML Name', 'xml literal - name',
        'CSS Selector', 'CSS Property Name', 'JSON Property Name',
    ],
}

# Token roles drawn with a neon glow in the dark themes: their colors are the keys of Glow/GlowPalette.cs.
GLOW_ROLES = ('keyword', 'type', 'function', 'tag', 'variable')

BAY = {
    'name': "Miami '26 Bay",
    'file': 'Miami26Bay.vstheme',
    'guid': '{222bdaa7-0725-4ee8-a26d-939951dacb78}',
    'base': 'dark',
    'glow': True,
    # adapt(): greys take this hue and saturation
    'neutral': (205, 0.20),
    # The bay at nightfall: a lilac blue sky, deep water, lavender palm trees on the status bar,
    # peach facades in the selection and pastel tokens.
    'colors': {
        'bg0': '0B1626', 'bg1': '0F2A30', 'bg2': '1C2747', 'bg3': '1F3448',
        'menu': '1A2D44', 'thumb': '345068', 'raised': '37506A', 'pressed': '2A4A60',
        'muted': '46607A', 'dim': '5F7C9A', 'text': 'EAF4F2',
        'accent': '2FA394', 'selection': '2FA394', 'accent_hover': '7FE0D2', 'accent_hot': '4CCFC0',
        'accent_soft': '9FE8DC', 'heading': 'F5B89C',
        'secondary': '6E6AC8', 'secondary_light': 'B5B2F0', 'secondary_mid': '908CE0', 'secondary_dark': '4A4790',
        'tertiary': 'B4607E', 'tertiary_light': 'F2A6B4', 'warm': 'F5B095',
        'status': '6763C2', 'status_text': 'FFFFFF', 'status_dark_text': '0B1626',
        'editor': '102230', 'editor_selection': '5A4048', 'editor_inactive_selection': '33333F',
        'line_number': '5F7C9A', 'caret': '7FD8C8', 'caret_secondary': 'F2A6B4', 'current_line': '17303C',
        'highlight': '33335E',
    },
    'tokens': {
        'keyword': '7FD8C8', 'type': 'A9A6F0', 'function': '8EC6EC', 'tag': 'F5B49C', 'variable': 'E2EEF2',
        'operator': '9FE3D6', 'attribute': '9CCBEA', 'string': 'F3DDB0', 'constant': 'F2A0B4',
        'comment': '64799C', 'escape': 'F0A0C8',
    },
}

BAY_LIGHT = {
    'name': "Miami '26 Bay Light",
    'file': 'Miami26BayLight.vstheme',
    'guid': '{ced9de59-6bf5-42c3-9f2d-d5c323ab90a9}',
    'base': 'light',
    'glow': False,
    # adapt(): the whites and greys of the base, by lightness. A sky blue frame, mint water panels and a sand
    # editor; lavender palm trees on the status bar and peach facades in the selection.
    'ramp': [(1.00, 'FBF3E6'), (0.975, 'D3EEE8'), (0.955, 'BFE3E2'), (0.93, 'A6CBE8'), (0.86, '93B8DC'),
             (0.80, '80AFC8'), (0.55, '58789A'), (0.42, '45627E'), (0.12, '1B3245'), (0.00, '0E2233')],
    'colors': {
        'text': '1B3245',
        'accent': '128079', 'accent_dark': '0E6A64', 'accent_darker': '0B5853', 'accent_hover': '1BA096',
        'accent_soft': '5FCFC2', 'selection': '17958B', 'accent_pale': 'B4E6DE', 'accent_wash': 'D5F1EC',
        'secondary': '6B67C2', 'tertiary': '7A76CC', 'tertiary_light': 'A9A6E8', 'warm': 'F4AE92',
        'status': '6B67C2', 'status_text': 'FFFFFF', 'status_dark_text': '1B3245',
        'editor': 'FBF3E6', 'editor_selection': 'F7CDBB', 'editor_inactive_selection': 'F2DFD2',
        'line_number': '7A93AE', 'caret': '128079', 'caret_secondary': 'C2416E', 'current_line': 'F2E6D3',
        'highlight': 'DCD9F6',
    },
    'tokens': {
        'keyword': '0E7A74', 'type': '5853B5', 'function': '23689E', 'tag': '9C3F8A', 'variable': '1F3A50',
        'operator': '2A7579', 'attribute': '23689E', 'string': 'B04F2A', 'constant': 'C2386C',
        'comment': '7380AA', 'escape': 'C2386C',
    },
}

SUNSET = {
    'name': "Miami '26 Sunset",
    'file': 'Miami26Sunset.vstheme',
    'guid': '{28fd2755-b519-4c54-aafb-3e1603f5bb44}',
    'base': 'dark',
    'glow': True,
    'neutral': (285, 0.24),
    # Dusk on the ocean front: a periwinkle night sky, plum palm trees, a peach horizon on the status bar
    # and a magenta accent.
    'colors': {
        'bg0': '160E24', 'bg1': '2A1A3E', 'bg2': '211B45', 'bg3': '33244C',
        'menu': '3A2A58', 'thumb': '503C70', 'raised': '5A447E', 'pressed': '6A2A5E',
        'muted': '5E4C7C', 'dim': '7E6A9C', 'text': 'F8EEF4',
        'accent': 'FF5FAA', 'selection': 'D9408A', 'accent_hover': 'FF8CC2', 'accent_hot': 'FF74B6',
        'accent_soft': 'FFA6CF', 'heading': 'FFC08A',
        'secondary': '6C78D8', 'secondary_light': 'A9B4F5', 'secondary_mid': '8E96E8', 'secondary_dark': '424A9C',
        'tertiary': 'C9662E', 'tertiary_light': 'FFB27A', 'warm': 'FF7A8A',
        'status': 'F5A872', 'status_text': '1E1430', 'status_dark_text': '1E1430',
        'editor': '231833', 'editor_selection': '5A2F62', 'editor_inactive_selection': '3A2A4E',
        'line_number': '7E6A9C', 'caret': 'FF5FAA', 'caret_secondary': 'FFB27A', 'current_line': '2E2042',
        'highlight': '3E3470',
    },
    'tokens': {
        'keyword': 'FF5FAA', 'type': 'A9B4F5', 'function': 'FFB27A', 'tag': 'D6A2F2', 'variable': 'F6E2EE',
        'operator': 'FF9CC8', 'attribute': 'FFBC8A', 'string': 'F6E2A2', 'constant': 'FF8A7A',
        'comment': '8C72A8', 'escape': '9AA6FF',
    },
}

SUNSET_LIGHT = {
    'name': "Miami '26 Sunset Light",
    'file': 'Miami26SunsetLight.vstheme',
    'guid': '{7f2e1cab-c836-4ff1-8ffd-dc2f89c11942}',
    'base': 'light',
    'glow': False,
    # The sky at dusk, from top to bottom: a periwinkle and lavender frame, pink panels and a peach editor;
    # plum palm trees on the status bar.
    'ramp': [(1.00, 'FDEBDB'), (0.975, 'F8D8E1'), (0.955, 'EECBE3'), (0.93, 'C9B9EA'), (0.86, 'AFA6E0'),
             (0.80, '9C96D6'), (0.55, '85709A'), (0.42, '6C5277'), (0.12, '2E1A3D'), (0.00, '1E0F2A')],
    'colors': {
        'text': '2E1A3D',
        'accent': 'C8287A', 'accent_dark': 'A61F64', 'accent_darker': '8A1A53', 'accent_hover': 'DE3E8E',
        'accent_soft': 'F08CBC', 'selection': 'D23A86', 'accent_pale': 'F6C2D8', 'accent_wash': 'FADCE6',
        'secondary': 'C2601F', 'tertiary': '5662C4', 'tertiary_light': '8E97E6', 'warm': 'F6A56E',
        'status': '7E4B87', 'status_text': 'FFFFFF', 'status_dark_text': '2E1A3D',
        'editor': 'FDEBDB', 'editor_selection': 'F6C4D8', 'editor_inactive_selection': 'F2D9E2',
        'line_number': '9A82A6', 'caret': 'C8287A', 'caret_secondary': '5662C4', 'current_line': 'F9DDD3',
        'highlight': 'DAD6F6',
    },
    'tokens': {
        'keyword': 'BE1F70', 'type': '4A56B8', 'function': 'A64F18', 'tag': '7A3D8C', 'variable': '35203F',
        'operator': 'A3306E', 'attribute': 'A9521C', 'string': '7F5E00', 'constant': 'B83A28',
        'comment': '8E7299', 'escape': '4A56B8',
    },
}

THEMES = [BAY, BAY_LIGHT, SUNSET, SUNSET_LIGHT]

# Marker read by the glow (Glow/GlowTheme.cs): only themes defining it glow.
GLOW_CATEGORY = '{a66c2731-f386-4130-813d-a705e4dc1880}'

CATEGORY = re.compile(r'(    <Category Name="[^"]*" GUID="(\{[^}]+\})">\r?\n)(.*?)(    </Category>\r?\n)', re.S)
COLOR = re.compile(r'      <Color Name="([^"]*)">\r?\n.*?      </Color>\r?\n', re.S)
COLOR_NAME = re.compile(r'<Color Name="([^"]*)">')
RAW = re.compile(r'(Type="CT_RAW" Source=")([0-9A-Fa-f]{2})([0-9A-Fa-f]{6})(")')
SLOT = {'Background': re.compile(r'<Background Type="[^"]*" Source="[^"]*" />'),
        'Foreground': re.compile(r'<Foreground Type="[^"]*" Source="[^"]*" />')}
NL = '\r\n'


def hls(rgb):
    return colorsys.rgb_to_hls(*(int(rgb[i:i + 2], 16) / 255 for i in (0, 2, 4)))


def to_rgb(h, l, s):
    return ''.join(f'{round(c * 255):02X}' for c in colorsys.hls_to_rgb(h % 1, l, s))


def chroma(rgb):
    channels = [int(rgb[i:i + 2], 16) for i in (0, 2, 4)]
    return max(channels) - min(channels)


def ramp(theme, lightness):
    """The color of the palette ramp at this lightness, interpolated between its stops."""
    stops = theme['ramp']
    for (l1, c1), (l2, c2) in zip(stops, stops[1:]):
        if l2 <= lightness <= l1:
            t = (lightness - l2) / (l1 - l2)
            return ''.join(f'{round(int(c2[i:i + 2], 16) + (int(c1[i:i + 2], 16) - int(c2[i:i + 2], 16)) * t):02X}'
                           for i in (0, 2, 4))
    return stops[0][1] if lightness > stops[0][0] else stops[-1][1]


def adapt(rgb, theme):
    """Colors of the base without a role: greys follow the palette (its 'ramp' in the light themes, its
    hue in the dark ones), blues move to its accent and purples to its tertiary color; reds, greens and
    yellows keep their meaning."""
    h, l, s = hls(rgb)
    hue = h * 360
    colors = theme['colors']
    if 'ramp' in theme and (chroma(rgb) < 24 or s < 0.12):
        return ramp(theme, l)
    if s < 0.12:
        if not 0.02 < l < 0.98:
            return rgb
        neutral_hue, neutral_sat = theme['neutral']
        return to_rgb(neutral_hue / 360, l, neutral_sat * (1 - abs(2 * l - 1)) ** 0.5)
    if 190 <= hue <= 225:
        return to_rgb(hls(colors['accent'])[0], l, s)
    if 250 <= hue <= 300:
        if theme['base'] == 'dark' and l < 0.45:  # the SynthWave night: take the hue of the palette backgrounds
            return to_rgb(hls(colors['bg2'])[0], l, s * 0.8)
        return to_rgb(hls(colors['tertiary'])[0], l, s)
    return rgb


def recolor_base(text, theme):
    roles = DARK_ROLES if theme['base'] == 'dark' else LIGHT_ROLES
    colors = theme['colors']

    def recolor(m):
        rgb = m.group(3).upper()
        new = colors[roles[rgb]] if rgb in roles else adapt(rgb, theme)
        return m.group(1) + m.group(2) + new + m.group(4)

    return RAW.sub(recolor, text)


def slot(kind, color):
    return f'<{kind} Type="CT_RAW" Source="FF{color}" />'


def set_color(block, background, foreground):
    for kind, color in (('Background', background), ('Foreground', foreground)):
        if color is None:
            continue
        if SLOT[kind].search(block):
            block = SLOT[kind].sub(slot(kind, color), block, count=1)
        else:
            block = block.replace('      </Color>', f'        {slot(kind, color)}{NL}      </Color>')
    return block


def new_color(name, background, foreground):
    return set_color(f'      <Color Name="{name}">{NL}      </Color>{NL}', background, foreground)


def set_colors(text, wanted):
    """Set {(category GUID, color name): (background, foreground)}, adding the missing colors and categories."""
    pending = dict(wanted)

    def recolor_category(m):
        header, guid, body, footer = m.groups()
        guid = guid.lower()

        def recolor_color(cm):
            key = (guid, cm.group(1))
            if key not in wanted:
                return cm.group(0)
            pending.pop(key, None)
            return set_color(cm.group(0), *wanted[key])

        body = COLOR.sub(recolor_color, body)
        # Colors this category does not have yet: add them to the first category with this GUID
        for key in [k for k in pending if k[0] == guid]:
            body += new_color(key[1], *pending.pop(key))
        return header + body + footer

    text = CATEGORY.sub(recolor_category, text)

    # Categories the base does not have at all
    added = ''
    for guid in dict.fromkeys(k[0] for k in pending):
        added += f'    <Category Name="{CATEGORY_NAMES[guid]}" GUID="{guid}">{NL}'
        added += ''.join(new_color(k[1], *pending[k]) for k in pending if k[0] == guid)
        added += f'    </Category>{NL}'
    i = text.rindex('  </Theme>')
    return text[:i] + added + text[i:]


def token_colors(theme):
    return {name: theme['tokens'][role] for role, names in TOKEN_ROLES.items() for name in names}


def editor_colors(theme):
    colors = theme['colors']
    wanted = {key: (colors[bg] if bg else None, colors[fg] if fg else None) for key, (bg, fg) in EDITOR.items()}
    # VS 2026 reads the token colors from the MEF category, and some of them (Keyword...) from the language
    # service one: set them in both, like the dark base does.
    names = language_service_names()
    for name, color in token_colors(theme).items():
        wanted[(MEF_ITEMS, name)] = (None, color)
        if name in names:
            wanted[(LANGUAGE_SERVICE_ITEMS, name)] = (None, color)
    return wanted


def language_service_names():
    """The token colors the dark base defines in the language service category."""
    text = DARK_BASE.read_text(encoding='utf-8-sig')
    category = next(m for m in CATEGORY.finditer(text) if m.group(2).lower() == LANGUAGE_SERVICE_ITEMS)
    return set(COLOR_NAME.findall(category.group(3)))


def without_glow_markers(text):
    """Drop the glow marker of the base, so that the SynthWave '84 glow never draws in Miami '26."""
    return CATEGORY.sub(lambda m: '' if m.group(1).startswith('    <Category Name="SynthWave"')
                        or m.group(2).lower() == GLOW_CATEGORY else m.group(0), text)


def with_glow_marker(text):
    marker = (f'    <Category Name="Miami26" GUID="{GLOW_CATEGORY}">{NL}'
              + new_color('NeonGlow', 'FFFFFF', None)
              + f'    </Category>{NL}')
    i = text.rindex('  </Theme>')
    return text[:i] + marker + text[i:]


def check_glow():
    """The glow is keyed by text color: glowing roles must use the colors of Glow/GlowPalette.cs, and no
    other role of a glowing theme may use one of them."""
    keys = {k.upper() for k in re.findall(r'\[Rgb\(0x([0-9A-Fa-f]{6})\)\]', GLOW_PALETTE.read_text(encoding='utf-8'))}
    for theme in THEMES:
        if not theme['glow']:
            continue
        for role, color in theme['tokens'].items():
            glowing = role in GLOW_ROLES
            assert (color.upper() in keys) == glowing, \
                f"{theme['name']}: {role} {color} {'is missing from' if glowing else 'is a key of'} {GLOW_PALETTE.name}"


def generate(theme):
    dark = theme['base'] == 'dark'
    text = (DARK_BASE if dark else LIGHT_BASE).read_text(encoding='utf-8-sig')
    text = without_glow_markers(text.replace('\r\n', '\n').replace('\n', NL))
    fallback = DARK_FALLBACK if dark else LIGHT_FALLBACK
    text, count = re.subn(r'<Theme Name="[^"]*" GUID="\{[^}]+\}"[^>]*>',
                          f'<Theme Name="{theme["name"]}" GUID="{theme["guid"]}" FallbackId="{fallback}">', text, count=1)
    assert count == 1
    text = recolor_base(text, theme)
    text = set_colors(text, editor_colors(theme))
    if theme['glow']:
        text = with_glow_marker(text)
    return text


def main():
    check_glow()
    for theme in THEMES:
        (ROOT / theme['file']).write_text(generate(theme), encoding='utf-8-sig', newline='')
        print(f"{theme['file']} generated")


if __name__ == '__main__':
    main()
