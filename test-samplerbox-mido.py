import mido, time

def MidiCallback(message):
    print('CALLBACK', message)
    print('RECEIVED in cb: ', midi_in[0].receive())

midi_in = []
previous = []
while True:
    all_ports = mido.get_input_names()
    for port_num,port in enumerate(all_ports):
        if port not in previous and 'Midi Through' not in port:
            print('new ports found in : ', all_ports)
            new_input = mido.open_input(port, callback=MidiCallback)
            midi_in.append(new_input)
            print('midi_in', midi_in)
            print('Opened MIDI: ' + str(port))
    previous = all_ports

    time.sleep(2)