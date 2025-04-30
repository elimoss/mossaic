import xml.etree.ElementTree as ET

class FontManager:
    def __init__(self, font_path):
        self.glyphs = self.load_svg_font(font_path)

    def load_svg_font(self, font_path):
        glyphs = {}

        tree = ET.parse(font_path)
        root = tree.getroot()

        for glyph in root.iter():
            if glyph.tag.endswith('glyph'):
                unicode_char = glyph.attrib.get('unicode')
                path_data = glyph.attrib.get('d')
                if unicode_char and path_data:
                    decoded_char = self.decode_unicode(unicode_char)
                    glyphs[decoded_char] = self.parse_path_data(path_data)

        # print(f"Loaded {len(glyphs)} glyphs.")
        return glyphs

    def decode_unicode(self, unicode_str):
        if unicode_str.startswith('&#x'):
            return chr(int(unicode_str[3:-1], 16))
        elif unicode_str.startswith('&#'):
            return chr(int(unicode_str[2:-1]))
        else:
            return unicode_str

    def parse_path_data(self, d):
        segments = []
        tokens = d.replace(',', ' ').split()
        i = 0
        current_pos = (0, 0)
        while i < len(tokens):
            cmd = tokens[i]
            if cmd.lower() == 'm':
                x = float(tokens[i+1])
                y = float(tokens[i+2])
                current_pos = (x, y)
                i += 3
            elif cmd.lower() == 'l':
                x = float(tokens[i+1])
                y = float(tokens[i+2])
                segments.append((current_pos, (x, y)))
                current_pos = (x, y)
                i += 3
            elif cmd.lower() == 'z':
                i += 1
            else:
                # print(f"Unknown SVG path command: {cmd}")
                i += 1
        return segments

    def get_glyph(self, char):
        return self.glyphs.get(char, None)
