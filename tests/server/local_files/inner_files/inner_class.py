import uuid


class InnerClass:
    def __init__(self):
        self.id = uuid.uuid4()

    def introduce(self):
        return self.id
