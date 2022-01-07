from abc import ABC, abstractmethod


class MasterchefInterface(ABC):

    @abstractmethod
    def initialize_escrow(self, escrow_address):
        pass

    @abstractmethod
    def deposit(self, _pid, _amount):
        pass

    @abstractmethod
    def withdraw(self, _pid, _amount):
        pass

    @abstractmethod
    def add(self):
        pass
