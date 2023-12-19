#-- Interface générale
import Gateway, mido
from debug import print_v

class MultiportGateway(Gateway):
    inport = []
    outport = []

    def send_midi(self, message, desc):
        print_v('output (%s): %s' % (desc, message))

        for port in outport:
            port.send(message)

    def connect_devices(self):
        global inport, outport
        print('input devices:', mido.get_input_names())
        print('output devices', mido.get_output_names())

        for port in inport:
            port.close()
        for port in outport:
            port.close()
        print('closed')

        for device_name in mido.get_input_names():
            inport.append(mido.open_input(device_name, callback=self.listen_input))
        for device_name in mido.get_output_names():
            outport.append(mido.open_output(device_name))