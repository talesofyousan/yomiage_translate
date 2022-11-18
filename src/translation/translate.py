import deepl
from pathlib import Path
import argparse

class DeeplTranslator():
    def __init__(self, auth_key) -> None:
        self.translator = deepl.Translator(auth_key)
        self.source_lang = 'EN'
        self.target_lang = 'JA'

    def translate_text(self, text):
        result = self.translator.translate_text(text, source_lang=self.source_lang, target_lang=self.target_lang)
        return result

def run(text_path : Path, auth_key:str, output_dir : Path):

    with open(text_path, 'r') as f:
        text = f.read()

    result = run_translator(text, auth_key)

    output_dir = output_dir / 'translation'
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    with open(output_dir / 'translated.txt', 'w') as f:
        f.write(result)


def run_translator(text: str, auth_key:str):
    translator = DeeplTranslator(auth_key)
    result = translator.translate_text(text)
    return str(result)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='翻訳モジュール')
    parser.add_argument('text_path', type=Path, help='翻訳したいテキストファイルパス')
    parser.add_argument('auth_key', type=str, help='翻訳APIのキー')
    parser.add_argument('--output_dir', type=Path, required=False, default='artifacts', help='出力テキストの保存先')
    args = parser.parse_args()

    run(**vars(args))