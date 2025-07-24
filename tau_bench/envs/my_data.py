class Data:
    def __init__(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def update_data(self, new_data):
        self.data = new_data

global_data = Data({})
