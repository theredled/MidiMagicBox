#https://readthedocs.org/projects/mido/downloads/pdf/latest/

import mido, time, traceback, sys, getopt, argparse

multiport = False
min_velocity = 30
max_velocity = 110
is_verbose = None
inport = [] if multiport else None
outport = [] if multiport else None
control_port = None
sustain_is_active = False

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

def listen_control(message):
    global min_velocity, max_velocity
    try:
        print_v('control input:', message)

        if message.type == 'note_on' and message.note == 36:
            time.sleep(2)
            connect_devices()
        elif message.type == 'control_change' and message.control == 1:
            min_velocity = message.value
        elif message.type == 'control_change' and  message.control == 2:
            max_velocity = message.value
        #-- save preset
        elif message.type == 'program_change' and sustain_is_active:

        #-- load preset
        elif message.type == 'program_change' and not sustain_is_active:


    except Exception as e:
        print('exception:', traceback.print_exception(e))

def listen_input(message):
    try:
        print_v('input:', message)

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
        inport = mido.open_input(device_name, callback=listen_input)
        outport = mido.open_output(device_name)
    if control_device_name:
        print('open control_port')
        control_port = mido.open_input(control_device_name, callback=listen_control)

    send_sysex_parameter(0x00, 0x06, 0, 'disable "Local control" for Reface CP')
    send_sysex_parameter(0x00, 0x0E, 1, 'enable "MIDI control" for Reface CP')
    send_sysex_parameter(0x30, 0x02, 2, 'wurli')

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


def main(argv):
    global is_verbose
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbosity', action="count",
                        help="increase output verbosity (e.g., -vv is more than -v)")
    args = parser.parse_args()
    is_verbose = args.verbosity

    connect_devices()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main(sys.argv[1:])