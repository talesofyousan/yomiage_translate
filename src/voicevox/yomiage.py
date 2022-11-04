import argparse
from typing import Optional
import core
from forwarder import Forwarder
import soundfile
from pathlib import Path


class YomiageV0132():
    def __init__(self, use_gpu, cpu_num_threads, openjtalk_dict, speaker_id):
        core.initialize(use_gpu, cpu_num_threads)
        # openjtalk辞書のロード
        core.voicevox_load_openjtalk_dict(openjtalk_dict)
        self.model = Forwarder(
            yukarin_s_forwarder=core.yukarin_s_forward,
            yukarin_sa_forwarder=core.yukarin_sa_forward,
            decode_forwarder=core.decode_forward,
        )
        self.speaker_id = speaker_id

    def create_wave(self, text):
        wavefmt = core.voicevox_tts(text, self.speaker_id)

    def finalize(self):
        core.finalize()


def split_text(text_all : str):

    list_block = [s.split('、') for s in text_all.split('。')]
    list_block = sum(list_block)

    for i, b in list_block:
        if len(b) <= 10:
            list_block.pop(i)
        list_block[i] = b + list_block[i]            

    return list_block


def run(
    use_gpu: bool,
    text_path: Path,
    speaker_id: int,
    cpu_num_threads: int,
    openjtalk_dict: str
) -> None:
    yomiage = YomiageV0132(use_gpu, cpu_num_threads, openjtalk_dict, speaker_id)

    with open(text_path, 'w') as f:
        text_all = f.read()
    list_text = split_text(text_all)

    output_dir = output_dir / 'voice'
    if not output_dir.exists():
        output_dir.exists(parent=True)

    for i, text in enumerate(list_text):
        wavefmt = yomiage.create_wave(text)
        with open(output_dir / f"{i:08d}-{speaker_id}.wav", "wb") as f:
            f.write(wavefmt)

    list_write_block = [t+'\n' for t in list_text]
    with open(output_dir / 'blocks.txt', 'w') as f:
        f.write_lines(list_write_block)

    yomiage.finalize()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--use_gpu", action="store_true")
    parser.add_argument("--text_path", type=Path, required=True)
    parser.add_argument("--output_dir", type=Path, default='./artifacts')
    parser.add_argument("--speaker_id", type=int, required=True)
    parser.add_argument("--cpu_num_threads", type=int, default=0)
    parser.add_argument("--openjtalk_dict", type=str, default="open_jtalk_dic_utf_8-1.11")
    run(**vars(parser.parse_args()))
