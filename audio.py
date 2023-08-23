
# audio.py

import sounddevice as sd
import numpy as np
import time as t

class Audio:
    def __init__(self, config):
        self.config = config
        self.is_recording = False
        self.stream = None
        self.input_device = None
        self.output_device = None

    def start_recording(self):
        self.is_recording = True
        self.stream = sd.InputStream(callback=self.audio_callback)
        self.stream.start()

    def stop_recording(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        self.is_recording = False

    def audio_callback(self, indata, frames, time, status):
        delay = self.config.get_delay()
        if delay > 0:
            t.sleep(delay / 1000.0)  # Convert delay from ms to seconds
        sd.play(indata, blocking=True, samplerate=self.config.samplerate, device=self.output_device)

    def set_input_device(self, device):
        self.input_device = device
        
    def set_output_device(self, device):
        self.output_device = device