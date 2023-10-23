from __future__ import annotations

import discord
import sounddevice as sd


class PCMStream(discord.AudioSource):
    def __init__(self, name):
        super().__init__()
        num = sd.query_devices(name, "input")["index"]  # type: ignore
        self.stream: sd.RawInputStream = sd.RawInputStream(
            device=num,
            samplerate=48000,
            channels=2,
            dtype="int16",
            latency="low",
        )
        self.frames = int(self.stream.samplerate / 50)
        self.stream.start()

    def __del__(self):
        self.stream.close()

    def read(self):
        if not self.stream:
            return

        data = self.stream.read(self.frames)[0]  # type: ignore
        return bytes(data)  # type: ignore
