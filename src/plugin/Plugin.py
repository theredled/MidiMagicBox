class Plugin:
    def __init__(self):
        self.gateway = None

    def set_gateway(self, obj):
        self.gateway = obj

    def listen_control(self, message):
        pass

    def listen_input(self, message):
        pass

    def register_listeners(self):
        pass

    def load_preset_data(self, data):
        return False

    def save_preset_data(self, data):
        return False

    def print_preset_content(self, data):
        pass

    def send_midi(self, message, desc):
        return self.gateway.send_midi(message, desc)

    def after_connect_device(self, is_input, device_name):
        pass

    def after_startup(self):
        pass