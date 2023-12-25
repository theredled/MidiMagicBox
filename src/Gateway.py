# -- Interface générale

import traceback, mido, argparse, time, sys

from . import debug
from .debug import print_v
from .plugin.Velocity import Velocity
from .plugin.RefaceCp import RefaceCp
from .plugin.Presets import Presets
from .plugin.SamplerBox import SamplerBox
from . import config
#import pydevd


class Gateway:
    def __init__(self):
        self.input_devices = {}
        self.output_devices = {}
        self.sustain_is_active = False
        self.plugins = []
        self.add_plugin(Velocity())
        self.add_plugin(RefaceCp())
        self.add_plugin(Presets())
        self.add_plugin(SamplerBox())

    def add_plugin(self, plugin):
        plugin.set_gateway(self)
        self.plugins.append(plugin)

    def send_midi(self, message, desc):
        print_v('output (%s): %s' % (desc, message))
        for device in self.output_devices:
            self.output_devices[device].send(message)

    def listen_control(self, message):
        if 'pydevd' in sys.modules:
            pydevd.settrace(suspend=False, trace_only_current_thread=True)
        try:
            if message.channel != config.CONTROL_MIDI_CHANNEL:
                return

            for p in self.plugins:
                result = p.listen_control(message)
                if result is True:
                    return
        except Exception as e:
            print('exception:', traceback.print_exception(e))

    def listen_input(self, message):
        if 'pydevd' in sys.modules:
            pydevd.settrace(suspend=False, trace_only_current_thread=True)
        try:
            print_v('input:', message)

            if message.channel == config.CONTROL_MIDI_CHANNEL:
                print_v('= control input')
                return self.listen_control(message)
            if message.channel != config.KEYBOARD_MIDI_CHANNEL:
                return

            print_v('= keyboard input')

            for p in self.plugins:
                result = p.listen_input(message)
                #print('result', p, result, isinstance(result, mido.Message))
                if result and isinstance(result, mido.Message):
                    message = result
                elif result is True:
                    return

            if message.type == 'sysex':
                return

            if message.type == 'control_change' and message.control == 64:
                self.sustain_is_active = message.value != 0
                print_v('sustain ', 'active' if self.sustain_is_active else 'inactive')

            self.send_midi(message, 'filtered')
        except Exception as e:
            print('exception:', traceback.print_exception(e))

    def find_new_devices(self, found_list, current_list):
        new_list = found_list - current_list
        new_list = list(filter(lambda name: ('Midi Through' not in name and 'RtMidi' not in name), new_list))
        return new_list

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbosity', action="count",
                            help="increase output verbosity (e.g., -vv is more than -v)")
        args = parser.parse_args()
        debug.is_verbose = args.verbosity

        for p in self.plugins:
            p.after_startup()

        while True:
            new_input_devices_names = self.find_new_devices(mido.get_input_names(), self.input_devices.keys())

            if len(new_input_devices_names):
                print('list mido devices', mido.get_input_names())
                for device_name in new_input_devices_names:
                    new_device = mido.open_input(device_name, callback=self.listen_input)
                    print('Opened MIDI input: ' + str(device_name))
                    self.input_devices[device_name] = new_device
                print('current input_devices', self.input_devices.keys())
                for p in self.plugins:
                    p.after_connect_device(True, new_input_devices_names)

            new_output_devices_names = self.find_new_devices(mido.get_output_names(), self.output_devices.keys())

            if len(new_output_devices_names):
                for device_name in new_output_devices_names:
                    new_device = mido.open_output(device_name)
                    print('Opened MIDI output: ' + str(device_name))
                    self.output_devices[device_name] = new_device
                for p in self.plugins:
                    p.after_connect_device(False, new_output_devices_names)

            time.sleep(2)
