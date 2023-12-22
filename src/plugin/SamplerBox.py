from . import Plugin
import mido, sys, math
from src.debug import print_v
import samplerbox_src.samplerbox as samplerbox

class SamplerBox(Plugin.Plugin):

    def __init__(self):
        samplerbox.init()
        super().__init__()
        self.enabled = False
        self.bank_number = None

    def listen_control(self, message):
        if message.type == 'control_change' and message.control == 4:
            self.enabled = message.value > 64
            if not self.enabled:
                return

            new_bank_number = math.floor((message.value - 64) / 10)
            if self.bank_number == new_bank_number:
                return

            self.bank_number = new_bank_number
            print_v('Sampler - Bank #%i' % self.bank_number)
            samplerbox.preset = self.bank_number
            samplerbox.load_samples()

    def listen_input(self, message):
        if message.type == 'note_on' and self.enabled:
            samplerbox.midi_callback((message.bytes(), None))
            return True

    def load_preset_data(self, data):
        if 'sampler_bank' in data and data['sampler_bank']:
            self.enabled = True
        else:
            self.enabled = False

    def save_preset_data(self, callback):
        callback({
            'sampler_bank': 2 if self.enabled else None
        })

