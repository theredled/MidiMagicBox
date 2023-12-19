import rtmidi, time

def MidiCallback(message, time_stamp):
    print(message)

midi_in = [rtmidi.MidiIn()]
previous = []
while True:
    all_ports = midi_in[0].get_ports()
    for port_num,port in enumerate(all_ports):
        if port not in previous and 'Midi Through' not in port:
            print('new ports found in : ', all_ports)
            midi_in.append(rtmidi.MidiIn())
            midi_in[-1].set_callback(MidiCallback)
            midi_in[-1].open_port(port_num)
            print('midi_in', midi_in)
            print('Opened MIDI: ' + str(port))
    previous = midi_in[0].get_ports()
    time.sleep(2)