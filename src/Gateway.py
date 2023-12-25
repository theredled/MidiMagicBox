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
        #self.inport = None
        #self.outport = None
        #self.control_port = None
        self.input_devices = {}
        self.output_devices = {}
        self.sustain_is_active = False
        #self.input_listeners = {}
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
            #print_v('control input:', message, message.type == 'program_change' and not self.sustain_is_active)
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
    '''
    def connect_devices(self):
        print('input devices:', mido.get_input_names())
        print('output devices', mido.get_output_names())

        device_name = ([item for item in mido.get_input_names() if item.startswith('reface CP')] or [None])[0]
        control_device_name = ([item for item in mido.get_input_names() if item.startswith('LPD8')] or [None])[0]
        # device_name = mido.get_input_names()[-1]
        print('using: ', device_name)

        if self.inport:
            print('close inport')
            self.inport.close()
        if self.outport:
            print('close outport')
            self.outport.close()
        if self.control_port:
            print('close control_port')
            self.control_port.close()
        print('closed')

        if device_name:
            print('open inport outport')
            self.inport = mido.open_input(device_name, callback=self.listen_input)
            self.outport = mido.open_output(device_name)
        if control_device_name:
            print('open control_port')
            self.control_port = mido.open_input(control_device_name, callback=self.listen_control)

        if not self.outport:
            print('No outport found')
            return
        if not self.inport:
            print('No inport found')
            return
        if not self.control_port:
            print('No control_port found')
            return
    '''

    def find_new_devices(self, found_list, current_list):
        new_list = found_list - current_list
        new_list = list(filter(lambda name: ('Midi Through' not in name), new_list))
        return new_list

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbosity', action="count",
                            help="increase output verbosity (e.g., -vv is more than -v)")
        args = parser.parse_args()
        debug.is_verbose = args.verbosity

        #self.connect_devices()

        for p in self.plugins:
            p.after_startup()

        while True:
            new_input_devices_names = self.find_new_devices(mido.get_input_names(), self.input_devices.keys())

            if len(new_input_devices_names):
                for device_name in new_input_devices_names:
                    new_device = mido.open_input(device_name, callback=self.listen_input)
                    print('Opened MIDI input: ' + str(device_name))
                    self.input_devices[device_name] = new_device
                for p in self.plugins:
                    p.after_connect_device(True, new_input_devices_names)

            new_output_devices_names = self.find_new_devices(mido.get_output_names(), self.output_devices.keys())

            if len(new_output_devices_names):
                for device_name in new_output_devices_names:
                    new_device = mido.open_output(device_name)
                    print('Opened MIDI output: ' + str(device_name))
                    self.output_devices[device_name] = new_device
                for p in self.plugins:
                    p.after_connect_device(False, new_input_devices_names)

            time.sleep(2)
