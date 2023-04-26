from abc import ABC, abstractmethod


class ProcessingModelBase(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def process_data(self, data):
        pass
