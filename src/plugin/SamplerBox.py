import src.plugin.Plugin as Plugin
import mido, sys
import samplerbox
#import "../../SamplerBox/src/samplerbox.py" as samplerbox

class SamplerBox(Plugin.Plugin):

    def __init__(self):
        super().__init__()
        self.enabled = False

    def listen_control(self, message):
        if message.type == 'control_change' and message.control == 4:
            self.enabled = message.value > 64

    def listen_input(self, message):
        if message.type == 'note_on' and self.enabled:
            samplerbox.MidiCallback((message.bytes(), None))
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


