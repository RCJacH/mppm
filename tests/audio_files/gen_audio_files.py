import os
import numpy as np
from soundfile import write


class Wavetable:
    def __init__(self, size=64):
        self.size = size

    def basewave(self):
        wave = np.linspace(0, 1, self.size, dtype=np.float32)
        wave %= 1 + np.finfo(np.float32).eps
        wave *= 2
        wave[wave > 1] -= 2
        return wave

    def sinwave(self):
        return np.sin(np.pi * self.basewave()[:-1])

    def plswave(self):
        width = 0
        pls = self.basewave()
        pls[np.where(pls < width)[0]] = -1.0
        pls[np.where(pls >= width)[0]] = 1.0
        return pls

    def triwave(self):
        return np.roll(2 * np.abs(self.basewave()[:-1]) - 1, -16)

    def empty(self):
        return np.abs(self.basewave()) * [0]

    def stereo(self, channelblocks):
        return np.array(channelblocks).transpose(1, 0)


class Generator:
    def path(self, filename, extension="wav"):
        return os.path.join("tests", "audio_files", filename + "." + extension)

    def set_pan(self, x, pct):
        pct = pct * 0.01
        mult = [abs(1 - pct), 1] if pct > 0 else [1, abs(pct)] if pct < 0 else [1, 1]
        return x * mult

    def get_wavetable(self, name):
        wt = Wavetable()
        if name == "sin-m" or name[-2] == ".":
            return wt.sinwave()
        elif name == "sin-s":
            return wt.stereo([wt.sinwave()] * 2)
        elif name == "0-m":
            return wt.empty()
        elif name == "0-s":
            return wt.stereo([wt.empty()] * 2)
        elif name == "sin+tri":
            return wt.stereo([wt.sinwave(), wt.triwave()])
        elif name == "sin-r100":
            return self.set_pan(self.get_wavetable("sin-s"), 100)
        elif name == "sin-l50":
            return self.set_pan(self.get_wavetable("sin-s"), -50)
        elif name == "sin-r25":
            return self.set_pan(self.get_wavetable("sin-s"), 25)
        elif name == "empty":
            return []
        return wt

    def write(self, name, sr=44100, subtype="PCM_24"):
        write(self.path(name), self.get_wavetable(name), sr, subtype)


if __name__ == "__main__":
    wt_gen = Generator()
    dirname = os.path.dirname(os.path.realpath(__file__))
    for f in os.listdir(dirname):
        if f.endswith(".wav"):
            os.remove(os.path.join(dirname, f))
    for name in [
        "sin-m",
        "sin-s",
        "sin.L",
        "sin.R",
        "0-m",
        "0-s",
        "sin+tri",
        "sin-r100",
        "sin-l50",
        "sin-r25",
        "empty",
    ]:
        wt_gen.write(name)
