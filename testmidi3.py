#https://readthedocs.org/projects/mido/downloads/pdf/latest/

import mido
import time

def listen_input(message):
    try:
        print('input:', message)
        print(1)
        filtered_on_message = message.copy(velocity=50)
        #output_message(filtered_on_message)
        print(2)
    except Exception as e:
        print(3, e)


inport = mido.open_input('reface CP', callback=listen_input)
outport = mido.open_output('reface CP')

while True:
    time.sleep(1)