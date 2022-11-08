import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2
import soundfile as sf
import numpy as np
# import moviepy as mpy
import moviepy.editor as mpy
import copy


class Frame():
    def __init__(self, text, audio_path, font_path, image_path=None, fps=24, interval_length=0.3) -> None:
        self.text = text
        self.font_path = font_path
        self.font_size = 24
        self.font_color = (0, 0, 0)
        self.line_length = 25
        self.fps = fps
        self.interval_length = interval_length
        if image_path is None:
            self.back = Image.new("RGB",(720, 480),(255,255,222))
        else:
            self.back = Image.open(image_path)
        self.set_audio(audio_path)

    @property
    def width(self):
        return self.back.width

    @property
    def height(self):
        return self.back.height

    def set_fint_size(self, font_size):
        self.font_size = font_size

    def render(self):
        self.frame_all = copy.copy(self.back)
        font = ImageFont.truetype(str(self.font_path), self.font_size)
        draw = ImageDraw.Draw(self.frame_all)

        text_multiline = ''
        for i in range(0, len(self.text), self.line_length):
            text_multiline += self.text[i: i+self.line_length]
            if i < len(self.text):
                text_multiline += '\n'
    
        w, h = draw.multiline_textsize(text_multiline, font)
        position = (int((self.width - w) / 2), int((self.height - h) / 2))
        draw.text(position, text_multiline, font=font, fill=self.font_color)

    @property
    def frame(self):
        return np.array(self.frame_all)

    def set_audio(self, audio_path: Path):
        data, sample_rate = sf.read(audio_path)
        self.sounddata = data
        self.sample_rate = sample_rate

    @property
    def audio_length(self):
        return len(self.sounddata) / self.sample_rate

    @property
    def num_frames(self):
        return (self.audio_length + self.interval_length) * self.fps

    @property
    def sound(self):
        return np.concatenate([self.sounddata, np.zeros((int(self.interval_length*self.sample_rate), ), dtype=np.float64)])


def decode_mp4(frames, output_path):
    clips = []
    for f in frames:
        f.render()
        frame = f.frame
        c = mpy.ImageClip(frame).set_duration(f.audio_length + f.interval_length)
        clips.append(c)

    clip = mpy.concatenate_videoclips(clips)
    s = np.concatenate([f.sound for f in frames])
    write_soundfile(s, frames[0].sample_rate, 'tmp.wav')
    audioclip = mpy.AudioFileClip("tmp.wav")
    audioclip.write_audiofile('tmp.mp3')
    # clip = clip.subclip()
    clip = clip.set_audio(audioclip)    
    clip.write_videofile(output_path, fps=frames[0].fps)


def write_soundfile(data, sample_rate, output_path):
    sf.write(output_path, data=data, samplerate=sample_rate)


def run(text_path: Path, audio_dir:Path, font_path: Path, output_dir: Path):

    output_dir = output_dir / 'video'
    if not output_dir.exists() :
        output_dir.mkdir(parents=True)

    with open(str(text_path), 'r') as f:
        list_block = [l[:-1] for l in f]

    list_audio_path = list(audio_dir.glob('*wav'))
    list_audio_path.sort()
    
    list_frames = [Frame(t, p, font_path) for t, p in zip(list_block, list_audio_path)]
    decode_mp4(list_frames, str(output_dir / 'yomiage.mp4'))


def test():
    audio_dir = Path('./src/inputs/')
    list_audio_path = list(audio_dir.glob('*wav'))
    fnt_path = './src/inputs/MPLUS1-Bold.ttf'

    frame1 = Frame('hoge', fnt_path)
    frame2 = Frame('hoge', fnt_path)
    frame3 = Frame('hoge', fnt_path)

    frame1.set_audio(list_audio_path[0])
    frame2.set_audio(list_audio_path[1])
    frame3.set_audio(list_audio_path[2])

    sound = np.concatenate([frame1.sound, frame2.sound, frame3.sound])
    sf.write('test.wav', data=sound, samplerate=24000)




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='動画生成モジュール')
    parser.add_argument('text_path', type=Path, help='テロップのパス')
    parser.add_argument('audio_dir', type=Path, help='wavファイルのパス')
    parser.add_argument('--font_path', type=Path, help='フォントパス', default='./src/inputs/MPLUS1-Bold.ttf')
    parser.add_argument('--output_dir', type=Path, required=False, default='artifacts', help='出力先')
    args = parser.parse_args()
    run(**vars(args))

    # test()