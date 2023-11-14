#https://readthedocs.org/projects/mido/downloads/pdf/latest/

import mido, time, traceback, sys, getopt, argparse

min_velocity = 30
max_velocity = 110
is_verbose = None
inport = None
outport = None
control_port = None

def output_message(message, desc):
    if is_verbose:
        print('output (%s): %s' % (desc, message))
    outport.send(message)

def listen_control(message):
    global min_velocity, max_velocity
    try:
        if is_verbose:
            print('control input:', message)

        if message.type == 'note_on' and message.note == 36:
            time.sleep(2)
            connect_devices()
        elif message.type == 'control_change' and message.control == 1:
            min_velocity = message.value
        elif message.type == 'control_change' and  message.control == 2:
            max_velocity = message.value

    except Exception as e:
        print('exception:', traceback.print_exception(e))


def listen_input(message):
    try:
        if is_verbose:
            print('input:', message)

        if message.type != 'note_on' or message.velocity == 0:
            output_message(message, 'bypassed')
            return

        #-- ALGO 1
        #velocity = min(max_velocity, max(message.velocity, min_velocity))
        #-- ALGO 2
        new_range = max_velocity - min_velocity
        new_velocity = round(min_velocity + new_range * (message.velocity/127))

        filtered_message = message.copy(velocity=new_velocity)
        output_message(filtered_message, 'changed')
    except Exception as e:
        print('exception:', traceback.print_exception(e))

def connect_devices():
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
    #disable_local_control_message = mido.Message('sysex', data=[0x06, 0x00])
    #outport.send(disable_local_control_message)


def main(argv):
    global is_verbose
    #opts = getopt.getopt(argv, 'v')
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