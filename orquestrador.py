import heapq
from Tarefa import Tarefa


class OrquestradorUsina:

    def __init__(self):
        self._fila: list    = []
        self._contador: int = 0  

    def enfileirar(self, tarefa: Tarefa) -> None:
        heapq.heappush(self._fila, (tarefa.prioridade.valor(), self._contador, tarefa))
        self._contador += 1
        print(f"✓ Enfileirada: {tarefa.__class__.__name__} [{tarefa.prioridade.nome()}]")

    def executar_proxima(self) -> None:
        if not self._fila:
            print("Fila vazia.")
            return

        _, _, tarefa = heapq.heappop(self._fila)
        print(f"\nExecutando: {tarefa.__class__.__name__} [{tarefa.prioridade.nome()}]")
        tarefa.executar()

    def executar_todas(self) -> None:
        if not self._fila:
            print("Fila vazia.")
            return

        print(f"\nExecutando {len(self._fila)} tarefa(s) na fila...\n")
        while self._fila:
            self.executar_proxima()

    def ver_status(self) -> None:
        if not self._fila:
            print("Fila vazia.")
            return

        print(f"\n{'─' * 50}")
        print(f"  FILA DE TAREFAS — {len(self._fila)} pendente(s)")
        print(f"{'─' * 50}")
        for prioridade, _, tarefa in sorted(self._fila):
            print(f"  [{tarefa.prioridade.nome():8}] {tarefa.__class__.__name__} — Reator {tarefa.id_reator}")
        print(f"{'─' * 50}\n")