from abc import ABC, abstractmethod
from Prioridade import Critica

class Evento:
    def __init__(self, descricao: str, critico: bool, id_reator: int):
        self.descricao = descricao
        self.critico = critico
        self.id_reator = id_reator


class Observador(ABC):
    @abstractmethod
    def atualizar(self, evento: Evento) -> None: ...


class Reator:
    def __init__(self, id_reator: int):
        self._id = id_reator
        self._observadores: list[Observador] = []

    @property
    def id(self) -> int:
        return self._id

    def inscrever(self, observador: Observador) -> None:
        self._observadores.append(observador)

    def _notificar(self, evento: Evento) -> None:
        for obs in self._observadores:
            obs.atualizar(evento)

    def processar(self, tarefa) -> None:
        evento = Evento(
            descricao=f"{type(tarefa).__name__} — {tarefa.resumo()}",
            critico=isinstance(tarefa.prioridade, Critica),
            id_reator=self._id,
        )
        self._notificar(evento)
