from Tarefa import Tarefa
from tarefas.monitoramento import MonitorarTemperatura, MonitorarRadiacao, MonitorarRefrigeracao
from tarefas.emergencia import DesligarReator, EvacuarPessoal
from tarefas.manutencao import AgendarManutencao, GerarRelatorio


class FabricaDeTarefas:

    _catalogo = {
        "monitorar_temperatura":  MonitorarTemperatura,
        "monitorar_radiacao":     MonitorarRadiacao,
        "monitorar_refrigeracao": MonitorarRefrigeracao,
        "desligar_reator":        DesligarReator,
        "evacuar_pessoal":        EvacuarPessoal,
        "agendar_manutencao":     AgendarManutencao,
        "gerar_relatorio":        GerarRelatorio,
    }

    @classmethod
    def criar(cls, tipo: str, **kwargs) -> Tarefa:
        if tipo not in cls._catalogo:
            raise ValueError(f"Tipo de tarefa desconhecido: '{tipo}'")

        classe = cls._catalogo[tipo]
        return classe(**kwargs)