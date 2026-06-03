from reator import Observador, Evento


class SistemaDeAlarme(Observador):
    def atualizar(self, evento: Evento) -> None:
        if evento.critico:
            print(f"ALARME [Reator {evento.id_reator}]: {evento.descricao}")


class PainelDeControle(Observador):
    def atualizar(self, evento: Evento) -> None:
        print(f"Painel [Reator {evento.id_reator}]: {evento.descricao}")
