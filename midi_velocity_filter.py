#https://readthedocs.org/projects/mido/downloads/pdf/latest/

import mido, time, traceback, sys, getopt, argparse
from functools import partial
import json
import os

multiport = False
min_velocity = 30
max_velocity = 110
is_verbose = None
inport = [] if multiport else None
outport = [] if multiport else None
control_port = None
sustain_is_active = False
presets = {}
presets_file_path = "presets.json"
input_listeners = {}
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

def send_midi(message, desc):
    if multiport:
        return send_midi_multiport(message, desc)

    print_v('output (%s): %s' % (desc, message))
    outport.send(message)

def print_v(*args):
    if is_verbose:
        print(*args)

def send_midi_multiport(message, desc):
    print_v('output (%s): %s' % (desc, message))

    for port in outport:
        port.send(message)

def save_preset_input_listener(preset_number, message):
    print_v('save_preset_input_listener', preset_number)
    if message.type != 'sysex':
        return
    if message.data[0] != 0x43 or message.data[7:10] != (0x30, 0, 0):
        return
    byte_count = message.data[5]
    param_data = message.data[10:25]
    for i, val in enumerate(param_data):
        print('Param ', reface_cp_parameters[i], val)

    write_preset(preset_number, {
        'sysex_params': param_data,
        'min_velocity': min_velocity,
        'max_velocity': max_velocity
    })

    del input_listeners['save_preset']
    return True

def write_preset(number, data):
    global presets
    print('Saving settings at preset #%i' % number)
    presets[str(number)] = data
    with open(presets_file_path, 'w') as fp:
        json.dump(presets, fp)


def retrieve_presets():
    global presets
    if not os.path.isfile(presets_file_path):
        print_v('No presets file')
        return
    with open(presets_file_path, 'r') as fp:
        presets = json.load(fp)
    print_v('Retrieved %i presets' % len(presets))


def save_preset(num):
    global input_listeners
    print_v('save_preset')
    send_sysex_parameter_dump_request('dump request')
    print_v('add to input_listeners')
    input_listeners['save_preset'] = partial(save_preset_input_listener, preset_number=num)
    return
    #-- Bulk Header

    #print('waiting for header', inport)
    #header_message = inport.receive()
    #print('header', header_message)
    ##-- Bulk Content
    #print('waiting for content')
    #content_message = inport.receive()
    #byte_count = content_message.data[5]
    #print('content_message', array_as_hex(content_message.data))
    #param_data = content_message.data[10:25]
    #print('param_data', param_data)
    #for i, val in enumerate(param_data):
    #    print('Param ', reface_cp_parameters[i], val)
    #-- Bulk Footer
    #print('waiting for footer')
    #footer_message = inport.receive()

def load_preset(num):
    global min_velocity, max_velocity
    print_v('load_preset', presets)
    preset = presets[str(num)]
    print('preset', preset)
    min_velocity = preset['min_velocity']
    max_velocity = preset['max_velocity']

    for i, val in enumerate(preset['sysex_params']):
        send_sysex_parameter(0x30, i, val)

    print('Loaded preset #%i' % num)
    #send_sysex_parameter_request(0x30, 0x02, 'request instr')

def listen_control(message):
    global min_velocity, max_velocity
    try:
        print_v('control input:', message, message.type == 'program_change' and not sustain_is_active)

        #if message.type == 'note_on' and message.note == 36:
        #    time.sleep(2)
        #    connect_devices()

        #-- Vélocité MIN
        if message.type == 'control_change' and message.control == 1:
            min_velocity = message.value
        #-- Vélocité MAX
        elif message.type == 'control_change' and  message.control == 2:
            max_velocity = message.value
        #-- Volume
        elif message.type == 'control_change' and  message.control == 3:
            send_sysex_parameter(0x30, 0, message.value)
        #-- Save preset
        elif message.type == 'program_change' and sustain_is_active:
            save_preset(message.program)
        #-- Load preset
        elif message.type == 'program_change' and not sustain_is_active:
            #save_preset(message.program)
            load_preset(message.program)

    except Exception as e:
        print('exception:', traceback.print_exception(e))

def array_as_hex(arr):
    return [hex(i) for i in arr]


def listen_input(message):
    global sustain_is_active
    try:
        print_v('input:', message)

        for key in input_listeners:
            if input_listeners[key](message=message) == True:
                return

        if message.type == 'sysex':
            #print_v('sysex input:', array_as_hex(message.data))
            return

        if message.type == 'control_change' and message.control == 64:
            sustain_is_active = message.value != 0
            print_v('sustain ', 'active' if sustain_is_active else 'inactive')

        if message.type != 'note_on' or message.velocity == 0:
            send_midi(message, 'bypassed')
            return

        #-- ALGO 1
        #velocity = min(max_velocity, max(message.velocity, min_velocity))
        #-- ALGO 2
        new_range = max_velocity - min_velocity
        new_velocity = round(min_velocity + new_range * (message.velocity/127))

        filtered_message = message.copy(velocity=new_velocity)
        send_midi(filtered_message, 'changed')
    except Exception as e:
        print('exception:', traceback.print_exception(e))

def connect_devices():
    if multiport:
        return connect_devices_multiport()

    global inport, outport, control_port
    print('input devices:', mido.get_input_names())
    print('output devices', mido.get_output_names())

    device_name = ([item for item in mido.get_input_names() if item.startswith('reface CP')] or [None])[0]
    control_device_name = ([item for item in mido.get_input_names() if item.startswith('LPD8')] or [None])[0]
    #device_name = mido.get_input_names()[-1]
    print('using: ', device_name)

    if inport:
        print('close inport')
        inport.close()
    if outport:
        print('close outport')
        outport.close()
    if control_port:
        print('close control_port')
        control_port.close()
    print('closed')

    if device_name:
        print('open inport outport')
        #inport = mido.open_input(device_name)
        inport = mido.open_input(device_name, callback=listen_input)
        #print('wait message')
        #message = inport.receive()
        #print('voila', message)

        outport = mido.open_output(device_name)
    if control_device_name:
        print('open control_port')
        control_port = mido.open_input(control_device_name, callback=listen_control)

    send_sysex_parameter(0x00, 0x06, 0, 'disable "Local control" for Reface CP')
    send_sysex_parameter(0x00, 0x0E, 1, 'enable "MIDI control" for Reface CP')
    #send_sysex_parameter(0x30, 0x00, 127, 'volume')
    #send_sysex_parameter_request(0x30, 0x02, 'request instr')

def connect_devices_multiport():
    global inport, outport
    print('input devices:', mido.get_input_names())
    print('output devices', mido.get_output_names())

    for port in inport:
        port.close()
    for port in outport:
        port.close()
    print('closed')

    for device_name in mido.get_input_names():
        inport.append(mido.open_input(device_name, callback=listen_input))
    for device_name in mido.get_output_names():
        outport.append(mido.open_output(device_name))


def send_sysex_parameter(addrHighByte, addrLowByte, data, desc = None):
    message = mido.parse([0xF0, 0x43, 0x10, 0x7F, 0x1C, 0x04, addrHighByte, 0x00, addrLowByte, data, 0xF7])
    send_midi(message, desc)

def send_sysex_parameter_dump_request(desc = None):
    message = mido.parse([0xF0, 0x43, 0x20, 0x7F, 0x1C, 0x04, 0x0E, 0x0F, 0x00, 0xF7])
    send_midi(message, desc)


def main(argv):
    global is_verbose
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbosity', action="count",
                        help="increase output verbosity (e.g., -vv is more than -v)")
    args = parser.parse_args()
    is_verbose = args.verbosity

    connect_devices()

    retrieve_presets()

    #save_preset(4)

    while True:
        #new_message = inport.receive()
        #listen_input(new_message)
        time.sleep(1)

if __name__ == "__main__":
    main(sys.argv[1:])