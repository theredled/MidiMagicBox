# -- Interface générale

import traceback, mido, argparse, time, sys
import src.debug as debug
from src.debug import print_v
import src.plugin.Velocity as Velocity
import src.plugin.RefaceCp as RefaceCp
import src.plugin.Presets as Presets
import src.plugin.SamplerBox as SamplerBox
#import pydevd


class Gateway:
    def __init__(self):
        self.inport = None
        self.outport = None
        self.control_port = None
        self.sustain_is_active = False
        self.input_listeners = {}
        self.plugins = []
        self.add_plugin(Velocity.Velocity())
        self.add_plugin(RefaceCp.RefaceCp())
        self.add_plugin(Presets.Presets())
        self.add_plugin(SamplerBox.SamplerBox())

    def add_plugin(self, plugin):
        plugin.set_gateway(self)
        self.plugins.append(plugin)

    def send_midi(self, message, desc):
        print_v('output (%s): %s' % (desc, message))
        self.outport.send(message)

    def listen_control(self, message):
        if 'pydevd' in sys.modules:
            pydevd.settrace(suspend=False, trace_only_current_thread=True)
        try:
            print_v('control input:', message, message.type == 'program_change' and not self.sustain_is_active)
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

        for p in self.plugins:
            p.after_connect_device()

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbosity', action="count",
                            help="increase output verbosity (e.g., -vv is more than -v)")
        args = parser.parse_args()
        debug.is_verbose = args.verbosity

        self.connect_devices()

        for p in self.plugins:
            p.after_startup()

        while True:
            time.sleep(1)
