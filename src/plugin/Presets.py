import src.plugin.Plugin as Plugin
from src.debug import print_v
import os, json
from functools import partial

from src.ClickSequence import ClickSequence

class Presets(Plugin.Plugin):

    def __init__(self):
        super().__init__()
        self.presets = {}
        self.presets_file_path = "presets.json"
        self.saving_preset = None
        self.dbl_click_sequence = ClickSequence(2)
        self.saving_pending_plugins = []

    def listen_control(self, message):
        # -- Save preset
        if message.type == 'program_change' and self.gateway.sustain_is_active:
            self.dbl_click_sequence.set_callback(lambda: self.save_preset(message.program))
            self.dbl_click_sequence.notify_click()

        # -- Load preset
        elif message.type == 'program_change' and not self.gateway.sustain_is_active:
            self.load_preset(message.program)

    def listen_input(self, message):
        pass

    def write_preset(self, number, data):
        print('Saving settings at preset #%i with content %s' % (number, data))
        self.print_content(data)
        self.presets[str(number)] = data
        with open(self.presets_file_path, 'w') as fp:
            json.dump(self.presets, fp)

    def retrieve_presets(self):
        if not os.path.isfile(self.presets_file_path):
            print('No presets file')
            return
        with open(self.presets_file_path, 'r') as fp:
            self.presets = json.load(fp)
        print('Retrieved %i presets' % len(self.presets))
        print_v(self.presets)

    def save_preset(self, num):
        print_v('save_preset')
        self.saving_preset = {'number': num}
        for p in self.gateway.plugins:
            self.saving_pending_plugins.append(p)
        for p in self.gateway.plugins:
            callback = partial(self.save_preset_callback, plugin=p)
            if p.save_preset_data(callback) is False:
                self.saving_pending_plugins.remove(p)
        print_v('after save_preset', self.saving_pending_plugins, self.saving_preset)

    def save_preset_callback(self, data, plugin):
        print_v('save_preset_callback', self.saving_pending_plugins, self.saving_preset)
        self.saving_pending_plugins.remove(plugin)
        self.saving_preset.update(data)
        if len(self.saving_pending_plugins) == 0:
            self.write_preset(self.saving_preset['number'], self.saving_preset)
            self.saving_preset = None

    def load_preset(self, num):
        print_v('load_preset', self.presets)
        try:
            preset = self.presets[str(num)] or None
        except KeyError:
            print('Preset %i not exists' % num)
            return
        print('Loading preset #%i with data %s' % (num, preset))
        for p in self.gateway.plugins:
            p.load_preset_data(preset)

        print('Loaded.')

    def print_content(self, data):
        for p in self.gateway.plugins:
            p.print_preset_content(data)

    def after_startup(self):
        self.retrieve_presets()

    #def after_connect_device(self, is_input, device_name):
    #    if not is_input:
    #        for p in self.gateway.plugins:
    #            p.reset_preset_data(data)

    
