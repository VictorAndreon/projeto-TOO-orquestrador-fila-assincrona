from abc import abstractmethod
from Tarefa import Tarefa
from Prioridade import Baixa


class TarefaManutencao(Tarefa):

    def __init__(self, id_reator: int, turno: str):
        super().__init__(id_reator, Baixa())
        self._turno = turno

    @property
    def turno(self) -> str:
        return self._turno

    @abstractmethod
    def executar(self) -> None: ...


class AgendarManutencao(TarefaManutencao):

    def __init__(self, id_reator: int, turno: str, data: str):
        super().__init__(id_reator, turno)
        self._data = data

    @property
    def data(self) -> str:
        return self._data

    def executar(self) -> None:
        print(f"[Reator {self._id_reator}] Manutenção agendada — turno: {self._turno} — data: {self._data}")


class GerarRelatorio(TarefaManutencao):

    def __init__(self, id_reator: int, turno: str):
        super().__init__(id_reator, turno)

    def executar(self) -> None:
        print(f"[Reator {self._id_reator}] Gerando relatório operacional — turno: {self._turno}")