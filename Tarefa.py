from abc import ABC, abstractmethod
from Prioridade import Prioridade

class Tarefa(ABC):
    def __init__(self, id_reator: int, prioridade: Prioridade):
        self._id_reator = id_reator
        self._prioridade = prioridade

    @property
    def id_reator(self) -> int:
        return self._id_reator
    
    @property
    def prioridade(self) -> Prioridade:
        return self._prioridade
    
    @prioridade.setter
    def prioridade(self, nova: Prioridade) -> None:
        self._prioridade = nova

    def resumo(self) -> str:
        return f"prioridade {self._prioridade.nome()}"