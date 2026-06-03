from abc import abstractmethod
from Tarefa import Tarefa
from Prioridade import Media, Alta


class TarefaMonitoramento(Tarefa):

    @abstractmethod
    def executar(self) -> None: ...


class MonitorarTemperatura(TarefaMonitoramento):

    def __init__(self, id_reator: int, limite: float):
        super().__init__(id_reator, Media())
        self._limite = limite

    @property
    def limite(self) -> float:
        return self._limite

    def executar(self) -> None:
        print(f"[Reator {self._id_reator}] Monitorando temperatura — limite: {self._limite}°C")


class MonitorarRadiacao(TarefaMonitoramento):

    def __init__(self, id_reator: int, nivel_max: float):
        super().__init__(id_reator, Alta())
        self._nivel_max = nivel_max

    @property
    def nivel_max(self) -> float:
        return self._nivel_max

    def executar(self) -> None:
        print(f"[Reator {self._id_reator}] Monitorando radiação — nível máximo: {self._nivel_max} mSv")


class MonitorarRefrigeracao(TarefaMonitoramento):

    def __init__(self, id_reator: int, pressao_min: float):
        super().__init__(id_reator, Alta())
        self._pressao_min = pressao_min

    @property
    def pressao_min(self) -> float:
        return self._pressao_min

    def executar(self) -> None:
        print(f"[Reator {self._id_reator}] Monitorando refrigeração — pressão mínima: {self._pressao_min} bar")