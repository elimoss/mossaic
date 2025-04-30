# plottext/text_generator.py

class TextGenerator:
    def __init__(self, text_path):
        with open(text_path, 'r', encoding='utf-8') as f:
            self.text = f.read().replace('\n', '')
        self.index = 0

    def next_char(self):
        if not self.text:
            return ' '  # fallback if empty

        char = self.text[self.index]
        self.index = (self.index + 1) % len(self.text)
        return char
