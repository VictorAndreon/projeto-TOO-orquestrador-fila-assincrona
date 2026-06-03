import io
import sys
from contextlib import redirect_stdout

from fabrica import FabricaDeTarefas
from orquestrador import OrquestradorUsina
from Prioridade import Critica, Alta, Media, Baixa
from tarefas.monitoramento import (
    MonitorarTemperatura,
    MonitorarRadiacao,
    MonitorarRefrigeracao,
)
from tarefas.emergencia import DesligarReator, EvacuarPessoal
from tarefas.manutencao import AgendarManutencao, GerarRelatorio
from reator import Reator, Evento, Observador
from observadores import SistemaDeAlarme, PainelDeControle

_total = 0
_falhas = 0

def executar_teste(funcao) -> None:
    """Roda um teste, captura AssertionError e imprime o resultado."""
    global _total, _falhas
    _total += 1
    descricao = (funcao.__doc__ or funcao.__name__).strip().splitlines()[0]
    try:
        funcao()
        print(f"  ✓ {descricao}")
    except AssertionError as e:
        _falhas += 1
        print(f"  ✗ FALHOU: {descricao}\n        → {e}")


def silenciar():
    """Context manager que descarta o stdout (oculta os prints de setup)."""
    return redirect_stdout(io.StringIO())


def ordem_de_execucao(orquestrador: OrquestradorUsina) -> list[str]:
    """Esvazia a fila e devolve, em ordem, o nome das classes executadas.

    Captura o stdout do orquestrador para inspecionar a ordem real de execução."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        orquestrador.executar_todas()

    nomes = []
    for linha in buffer.getvalue().splitlines():
        if "Executando:" in linha:
            nome = linha.split("Executando:")[1].split("[")[0].strip()
            nomes.append(nome)
    return nomes


class ObservadorEspiao(Observador):
    """Observer de teste: grava os eventos recebidos para inspeção nos asserts."""

    def __init__(self):
        self.eventos = []

    def atualizar(self, evento: Evento) -> None:
        self.eventos.append(evento)


#  1. FÁBRICA DE TAREFAS (padrão Factory)
def test_factory_cria_classe_correta():
    """Factory devolve a classe concreta certa para cada tipo do catálogo"""
    casos = [
        (FabricaDeTarefas.criar("monitorar_temperatura", id_reator=1, limite=350.0), MonitorarTemperatura),
        (FabricaDeTarefas.criar("monitorar_radiacao", id_reator=1, nivel_max=5.0), MonitorarRadiacao),
        (FabricaDeTarefas.criar("monitorar_refrigeracao", id_reator=1, pressao_min=2.0), MonitorarRefrigeracao),
        (FabricaDeTarefas.criar("desligar_reator", id_reator=1, motivo="x"), DesligarReator),
        (FabricaDeTarefas.criar("evacuar_pessoal", id_reator=1, motivo="x", zona="A"), EvacuarPessoal),
        (FabricaDeTarefas.criar("agendar_manutencao", id_reator=1, turno="manhã", data="01/01/2026"), AgendarManutencao),
        (FabricaDeTarefas.criar("gerar_relatorio", id_reator=1, turno="manhã"), GerarRelatorio),
    ]
    for tarefa, classe_esperada in casos:
        assert isinstance(tarefa, classe_esperada), (
            f"esperava {classe_esperada.__name__}, veio {type(tarefa).__name__}"
        )


def test_factory_atribui_prioridade_correta():
    """Cada tipo de tarefa nasce com a prioridade de negócio esperada"""
    esperado = [
        ("monitorar_temperatura", dict(id_reator=1, limite=350.0), "MÉDIA"),
        ("monitorar_radiacao", dict(id_reator=1, nivel_max=5.0), "ALTA"),
        ("monitorar_refrigeracao", dict(id_reator=1, pressao_min=2.0), "ALTA"),
        ("desligar_reator", dict(id_reator=1, motivo="x"), "CRÍTICA"),
        ("evacuar_pessoal", dict(id_reator=1, motivo="x", zona="A"), "CRÍTICA"),
        ("agendar_manutencao", dict(id_reator=1, turno="manhã", data="01/01/2026"), "BAIXA"),
        ("gerar_relatorio", dict(id_reator=1, turno="manhã"), "BAIXA"),
    ]
    for tipo, kwargs, nome_prioridade in esperado:
        tarefa = FabricaDeTarefas.criar(tipo, **kwargs)
        assert tarefa.prioridade.nome() == nome_prioridade, (
            f"{tipo}: esperava prioridade {nome_prioridade}, veio {tarefa.prioridade.nome()}"
        )


def test_factory_repassa_kwargs():
    """Os **kwargs chegam intactos ao construtor de cada tarefa"""
    temp = FabricaDeTarefas.criar("monitorar_temperatura", id_reator=7, limite=412.5)
    assert temp.id_reator == 7
    assert temp.limite == 412.5

    evac = FabricaDeTarefas.criar("evacuar_pessoal", id_reator=3, motivo="vazamento", zona="Setor B")
    assert evac.motivo == "vazamento"
    assert evac.zona == "Setor B"

    manut = FabricaDeTarefas.criar("agendar_manutencao", id_reator=2, turno="noite", data="15/07/2026")
    assert manut.turno == "noite"
    assert manut.data == "15/07/2026"


def test_factory_tipo_invalido_lanca_erro():
    """Tipo fora do catálogo levanta ValueError (falha cedo e clara)"""
    try:
        FabricaDeTarefas.criar("tipo_que_nao_existe", id_reator=1)
        assert False, "deveria ter levantado ValueError para tipo desconhecido"
    except ValueError:
        pass  # comportamento esperado


#  2. PRIORIDADES
def test_prioridades_valores_e_nomes():
    """Cada prioridade tem o valor e o nome corretos"""
    assert (Critica().valor(), Critica().nome()) == (0, "CRÍTICA")
    assert (Alta().valor(), Alta().nome()) == (1, "ALTA")
    assert (Media().valor(), Media().nome()) == (2, "MÉDIA")
    assert (Baixa().valor(), Baixa().nome()) == (3, "BAIXA")


def test_prioridades_ordenam_do_mais_urgente_ao_menos():
    """Menor valor = mais urgente (Crítica < Alta < Média < Baixa)"""
    valores = [Critica().valor(), Alta().valor(), Media().valor(), Baixa().valor()]
    assert valores == sorted(valores), "os valores não estão em ordem crescente de urgência"
    assert len(set(valores)) == 4, "há prioridades com o mesmo valor"


#  3. ORQUESTRADOR (fila por prioridade)
def test_orquestrador_executa_por_prioridade():
    """Fila executa da prioridade mais alta para a mais baixa, fora da ordem de entrada"""
    orq = OrquestradorUsina()
    # Enfileira de propósito FORA de ordem de prioridade:
    with silenciar():
        orq.enfileirar(FabricaDeTarefas.criar("gerar_relatorio", id_reator=1, turno="manhã"))      # BAIXA
        orq.enfileirar(FabricaDeTarefas.criar("desligar_reator", id_reator=1, motivo="falha"))     # CRÍTICA
        orq.enfileirar(FabricaDeTarefas.criar("monitorar_temperatura", id_reator=1, limite=350.0)) # MÉDIA
        orq.enfileirar(FabricaDeTarefas.criar("monitorar_radiacao", id_reator=1, nivel_max=5.0))   # ALTA

    ordem = ordem_de_execucao(orq)
    assert ordem == [
        "DesligarReator",        # CRÍTICA (0)
        "MonitorarRadiacao",     # ALTA    (1)
        "MonitorarTemperatura",  # MÉDIA   (2)
        "GerarRelatorio",        # BAIXA   (3)
    ], f"ordem de execução inesperada: {ordem}"


def test_orquestrador_mantem_fifo_no_empate():
    """Tarefas de mesma prioridade saem na ordem de chegada (desempate FIFO)"""
    orq = OrquestradorUsina()
    # Duas tarefas BAIXA: a primeira a entrar deve ser a primeira a sair.
    with silenciar():
        orq.enfileirar(FabricaDeTarefas.criar("gerar_relatorio", id_reator=1, turno="manhã"))
        orq.enfileirar(FabricaDeTarefas.criar("agendar_manutencao", id_reator=1, turno="tarde", data="01/02/2026"))

    ordem = ordem_de_execucao(orq)
    assert ordem == ["GerarRelatorio", "AgendarManutencao"], (
        f"o desempate FIFO falhou: {ordem}"
    )


def test_orquestrador_fila_vazia():
    """Executar com a fila vazia não quebra e avisa o usuário"""
    orq = OrquestradorUsina()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        orq.executar_proxima()
    assert "Fila vazia." in buffer.getvalue()


#  4. RESUMO (método polimórfico para o painel)
def test_resumo_override_traz_o_valor():
    """resumo() traz o valor da tarefa nas classes que sobrescrevem (override)"""
    assert MonitorarTemperatura(id_reator=1, limite=350.0).resumo() == "limite 350.0°C"
    assert MonitorarRadiacao(id_reator=1, nivel_max=5.0).resumo() == "nível máx 5.0 mSv"
    assert MonitorarRefrigeracao(id_reator=1, pressao_min=2.0).resumo() == "pressão mín 2.0 bar"
    assert DesligarReator(id_reator=1, motivo="vazamento").resumo() == "motivo: vazamento"
    assert EvacuarPessoal(id_reator=1, motivo="fuga", zona="B").resumo() == "zona B — fuga"


def test_resumo_default_usa_a_prioridade():
    """Tarefas sem override caem no resumo() padrão da base Tarefa"""
    assert GerarRelatorio(id_reator=1, turno="manhã").resumo() == "prioridade BAIXA"
    assert AgendarManutencao(id_reator=1, turno="tarde", data="01/01/2026").resumo() == "prioridade BAIXA"


#  5. OBSERVER (Reator notifica observers ao enfileirar)
def test_observer_emergencia_dispara_evento_critico():
    """Enfileirar uma emergência gera um evento crítico para os observers"""
    espiao = ObservadorEspiao()
    orq = OrquestradorUsina(observadores=[espiao])
    with silenciar():
        orq.enfileirar(FabricaDeTarefas.criar("desligar_reator", id_reator=1, motivo="vazamento"))
    assert len(espiao.eventos) == 1, f"esperava 1 evento, veio {len(espiao.eventos)}"
    assert espiao.eventos[0].critico is True
    assert espiao.eventos[0].id_reator == 1


def test_observer_monitoramento_nao_e_critico_e_traz_resumo():
    """Tarefa de monitoramento gera evento não-crítico com o resumo no texto"""
    espiao = ObservadorEspiao()
    orq = OrquestradorUsina(observadores=[espiao])
    with silenciar():
        orq.enfileirar(FabricaDeTarefas.criar("monitorar_temperatura", id_reator=2, limite=350.0))
    evento = espiao.eventos[0]
    assert evento.critico is False
    assert "limite 350.0°C" in evento.descricao, f"resumo ausente em: {evento.descricao}"


def test_observer_notifica_todos_os_observers():
    """Todos os observers inscritos recebem o evento (um-para-muitos)"""
    a, b = ObservadorEspiao(), ObservadorEspiao()
    orq = OrquestradorUsina(observadores=[a, b])
    with silenciar():
        orq.enfileirar(FabricaDeTarefas.criar("desligar_reator", id_reator=1, motivo="x"))
    assert len(a.eventos) == 1 and len(b.eventos) == 1, "nem todos os observers foram notificados"


def test_observer_reator_reutilizado_por_id():
    """Tarefas do mesmo reator reutilizam o mesmo objeto Reator (subject)"""
    espiao = ObservadorEspiao()
    orq = OrquestradorUsina(observadores=[espiao])
    with silenciar():
        orq.enfileirar(FabricaDeTarefas.criar("gerar_relatorio", id_reator=5, turno="manhã"))
        orq.enfileirar(FabricaDeTarefas.criar("monitorar_radiacao", id_reator=5, nivel_max=4.0))
    assert orq._reator(5) is orq._reator(5), "o reator não foi reutilizado por id"
    assert len(espiao.eventos) == 2
    assert all(e.id_reator == 5 for e in espiao.eventos)


def test_alarme_so_reage_a_critico_painel_sempre():
    """SistemaDeAlarme dispara só em crítico; PainelDeControle exibe sempre"""
    orq = OrquestradorUsina(observadores=[SistemaDeAlarme(), PainelDeControle()])
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        orq.enfileirar(FabricaDeTarefas.criar("monitorar_temperatura", id_reator=1, limite=350.0))
        orq.enfileirar(FabricaDeTarefas.criar("desligar_reator", id_reator=1, motivo="falha"))
    saida = buffer.getvalue()
    assert saida.count("Painel") == 2, "o painel deveria exibir as duas tarefas"
    assert saida.count("ALARME") == 1, "o alarme deveria disparar só na emergência"


#  Execução
TESTES = [
    test_factory_cria_classe_correta,
    test_factory_atribui_prioridade_correta,
    test_factory_repassa_kwargs,
    test_factory_tipo_invalido_lanca_erro,
    test_prioridades_valores_e_nomes,
    test_prioridades_ordenam_do_mais_urgente_ao_menos,
    test_orquestrador_executa_por_prioridade,
    test_orquestrador_mantem_fifo_no_empate,
    test_orquestrador_fila_vazia,
    test_resumo_override_traz_o_valor,
    test_resumo_default_usa_a_prioridade,
    test_observer_emergencia_dispara_evento_critico,
    test_observer_monitoramento_nao_e_critico_e_traz_resumo,
    test_observer_notifica_todos_os_observers,
    test_observer_reator_reutilizado_por_id,
    test_alarme_so_reage_a_critico_painel_sempre,
]


if __name__ == "__main__":
    print("═" * 60)
    print("  TESTES — Sistema de Controle da Usina Nuclear")
    print("═" * 60)

    for teste in TESTES:
        executar_teste(teste)

    print("─" * 60)
    passou = _total - _falhas
    if _falhas == 0:
        print(f"Todos os {_total} testes passaram!")
        sys.exit(0)
    else:
        print(f"{_falhas} de {_total} teste(s) falharam ({passou} ok).")
        sys.exit(1)
