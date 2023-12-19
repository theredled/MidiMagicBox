import src.plugin.Plugin as Plugin
import mido
from src.debug import print_v


class RefaceCp(Plugin.Plugin):
    reface_cp_parameters = {
        0x00: 'Vol',
        0x01: '--',
        0x02: 'Inst',
        0x03: 'Drive',
        0x04: '1Type',
        0x05: '1Depth',
        0x06: '1Rate',
        0x07: '2Type',
        0x08: '2Depth',
        0x09: '2Speed',
        0x0A: '3Type',
        0x0B: '3Depth',
        0x0C: '3Time',
        0x0D: 'Reverb',
        0x0E: '--',
        0x0F: '--'
    }

    def __init__(self):
        super().__init__()
        self.pending_save_preset_callback = None

    def dump_sysex_params(self, param_data):
        for i, val in enumerate(param_data):
            print('Param ', self.reface_cp_parameters[i], val)

    def send_sysex_parameter(self, addr_high_byte, addr_low_byte, data, desc=None):
        message = mido.parse([
            0xF0,  # SYSEX
            0x43,  # Yahama ID
            0x10,  # 1=Param Change, 0=Device number (?)
            0x7F,  # Group Number High (?)
            0x1C,  # Group Number Low (?)
            0x04,  # Model ID (=CP)
            addr_high_byte,  # Param addr
            0x00,
            addr_low_byte,
            data,  # Value
            0xF7  # END SYSEX
        ])
        self.send_midi(message, desc)

    def send_sysex_parameter_dump_request(self, desc=None):
        message = mido.parse([
            0xF0,  # SYSEX etc
            0x43,
            0x20,  # 2=Dump Request
            0x7F,
            0x1C,
            0x04,  # Model ID (=CP)
            0x0E,  # Addr (?)
            0x0F,
            0x00,
            0xF7
        ])
        self.send_midi(message, desc)

    def listen_control(self, message):
        # -- Volume
        if message.type == 'control_change' and message.control == 3:
            self.send_sysex_parameter(0x30, 0, message.value)

    def listen_input(self, message):
        if not self.pending_save_preset_callback:
            return
        if message.type != 'sysex':
            return
        if message.data[0] != 0x43 or message.data[7:10] != (0x30, 0, 0):
            return
        param_data = message.data[10:25]

        self.pending_save_preset_callback({'sysex_params': param_data})
        self.pending_save_preset_callback = None
        return True

    def load_preset_data(self, data):
        if 'sysex_params' not in data:
            return
        for i, val in enumerate(data['sysex_params']):
            self.send_sysex_parameter(0x30, i, val)

        # -- Volume, doit être passé à la fin
        self.send_sysex_parameter(0x30, 0, data['sysex_params'][0])

        self.dump_sysex_params(data['sysex_params'])

    def save_preset_data(self, callback):
        self.send_sysex_parameter_dump_request('dump request')
        self.pending_save_preset_callback = callback

    def print_preset_content(self, data):
        self.dump_sysex_params(data)

    def after_connect_device(self):
        self.send_sysex_parameter(0x00, 0x06, 0, 'disable "Local control" for Reface CP')
        self.send_sysex_parameter(0x00, 0x0E, 1, 'enable "MIDI control" for Reface CP')
