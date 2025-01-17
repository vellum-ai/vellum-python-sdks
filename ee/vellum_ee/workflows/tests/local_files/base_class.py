from uuid import uuid4

from .inner_files.inner_class import InnerClass


class BaseClass:
    result = None

    def __init__(self):
        self.id = uuid4()
        self.inner_class = InnerClass

    def run(self):
        self.result = self.inner_class().introduce()
        return self.result
