from abc import abstractmethod
from Tarefa import Tarefa
from Prioridade import Critica


class TarefaEmergencia(Tarefa):

    def __init__(self, id_reator: int, motivo: str):
        super().__init__(id_reator, Critica())
        self._motivo = motivo

    @property
    def motivo(self) -> str:
        return self._motivo

    @abstractmethod
    def executar(self) -> None: ...


class DesligarReator(TarefaEmergencia):

    def __init__(self, id_reator: int, motivo: str):
        super().__init__(id_reator, motivo)

    def resumo(self) -> str:
        return f"motivo: {self._motivo}"

    def executar(self) -> None:
        print(f"[Reator {self._id_reator}] DESLIGAMENTO DE EMERGÊNCIA — motivo: {self._motivo}")


class EvacuarPessoal(TarefaEmergencia):

    def __init__(self, id_reator: int, motivo: str, zona: str):
        super().__init__(id_reator, motivo)
        self._zona = zona

    @property
    def zona(self) -> str:
        return self._zona

    def resumo(self) -> str:
        return f"zona {self._zona} — {self._motivo}"

    def executar(self) -> None:
        print(f"[Reator {self._id_reator}] EVACUAÇÃO — zona: {self._zona} — motivo: {self._motivo}")