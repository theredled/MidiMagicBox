import src.plugin.Plugin as Plugin
from src.debug import print_v

class Velocity(Plugin.Plugin):
    def __init__(self):
        super().__init__()
        self.min_velocity = 30
        self.max_velocity = 110
        #self.last_manual_min_velocity = 30
        #self.last_manual_max_velocity = 110

    @property
    def min_velocity(self):
        return self._min_velocity

    @min_velocity.setter
    def min_velocity(self, value):
        print_v('set min_velocity', value)
        self._min_velocity = value
        
    def listen_control(self, message):
        # -- Vélocité MIN
        if message.type == 'control_change' and message.control == 1:
            self.min_velocity = message.value
        # -- Vélocité MAX
        elif message.type == 'control_change' and message.control == 2:
            self.max_velocity = message.value

    def listen_input(self, message):
        if message.type != 'note_on' or message.velocity == 0:
            return

        # -- ALGO 2
        new_range = self.max_velocity - self.min_velocity
        new_velocity = round(self.min_velocity + new_range * (message.velocity / 127))

        filtered_message = message.copy(velocity=new_velocity)
        # self.send_midi(filtered_message, 'changed')
        return filtered_message

    def register_listeners(self):
        pass

    def load_preset_data(self, data):
        print_v('vel load_preset_data', data)
        self.min_velocity = data['min_velocity']
        self.max_velocity = data['max_velocity']

    def save_preset_data(self, callback):
        callback({
            'min_velocity': self.min_velocity,
            'max_velocity': self.max_velocity
        })

    def print_preset_content(self, data):
        print('Velocity : %i > %i' % (data['min_velocity'], data['max_velocity']))
