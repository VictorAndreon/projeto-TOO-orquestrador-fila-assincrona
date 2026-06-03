from abc import ABC, abstractmethod

class Prioridade(ABC):
    @abstractmethod
    def valor(self) -> int: 
        pass

    @abstractmethod
    def nome(self) -> str: 
        pass

class Critica(Prioridade):
    def valor(self) -> int: 
        return 0
    def nome(self) -> str:  
        return "CRÍTICA"

class Alta(Prioridade):
    def valor(self) -> int: 
        return 1
    def nome(self) -> str:  
        return "ALTA"

class Media(Prioridade):
    def valor(self) -> int: 
        return 2
    def nome(self) -> str:  
        return "MÉDIA"

class Baixa(Prioridade):
    def valor(self) -> int: 
        return 3
    def nome(self) -> str:  
        return "BAIXA"