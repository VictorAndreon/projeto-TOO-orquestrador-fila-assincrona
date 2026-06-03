from orquestrador import OrquestradorUsina
from fabrica import FabricaDeTarefas


def menu_principal(orquestrador: OrquestradorUsina) -> None:
    while True:
        print(f"\n{'═' * 50}")
        print("  USINA NUCLEAR — SISTEMA DE CONTROLE")
        print(f"{'═' * 50}")
        print("  1. Adicionar tarefa à fila")
        print("  2. Executar próxima tarefa")
        print("  3. Executar todas as tarefas")
        print("  4. Ver status da fila")
        print("  0. Sair")
        print(f"{'═' * 50}")

        opcao = input("\n  Opção: ").strip()

        if opcao == "1":
            menu_adicionar(orquestrador)
        elif opcao == "2":
            orquestrador.executar_proxima()
        elif opcao == "3":
            orquestrador.executar_todas()
        elif opcao == "4":
            orquestrador.ver_status()
        elif opcao == "0":
            print("\n  Encerrando sistema...\n")
            break
        else:
            print("\n  Opção inválida.")


def menu_adicionar(orquestrador: OrquestradorUsina) -> None:
    print(f"\n{'─' * 50}")
    print("  SELECIONAR TAREFA")
    print(f"{'─' * 50}")
    print("  --- Monitoramento ---")
    print("  1. Monitorar temperatura")
    print("  2. Monitorar radiação")
    print("  3. Monitorar refrigeração")
    print("  --- Emergência ---")
    print("  4. Desligar reator")
    print("  5. Evacuar pessoal")
    print("  --- Manutenção ---")
    print("  6. Agendar manutenção")
    print("  7. Gerar relatório")
    print("  0. Voltar")
    print(f"{'─' * 50}")

    opcao = input("\n  Opção: ").strip()

    if opcao == "0":
        return

    try:
        tarefa = None

        if opcao == "1":
            id_reator = int(input("  ID do reator: "))
            limite    = float(input("  Limite de temperatura (°C): "))
            tarefa    = FabricaDeTarefas.criar("monitorar_temperatura", id_reator=id_reator, limite=limite)

        elif opcao == "2":
            id_reator  = int(input("  ID do reator: "))
            nivel_max  = float(input("  Nível máximo de radiação (mSv): "))
            tarefa     = FabricaDeTarefas.criar("monitorar_radiacao", id_reator=id_reator, nivel_max=nivel_max)

        elif opcao == "3":
            id_reator   = int(input("  ID do reator: "))
            pressao_min = float(input("  Pressão mínima (bar): "))
            tarefa      = FabricaDeTarefas.criar("monitorar_refrigeracao", id_reator=id_reator, pressao_min=pressao_min)

        elif opcao == "4":
            id_reator = int(input("  ID do reator: "))
            motivo    = input("  Motivo: ")
            tarefa    = FabricaDeTarefas.criar("desligar_reator", id_reator=id_reator, motivo=motivo)

        elif opcao == "5":
            id_reator = int(input("  ID do reator: "))
            motivo    = input("  Motivo: ")
            zona      = input("  Zona de evacuação: ")
            tarefa    = FabricaDeTarefas.criar("evacuar_pessoal", id_reator=id_reator, motivo=motivo, zona=zona)

        elif opcao == "6":
            id_reator = int(input("  ID do reator: "))
            turno     = input("  Turno (manhã/tarde/noite): ")
            data      = input("  Data (dd/mm/aaaa): ")
            tarefa    = FabricaDeTarefas.criar("agendar_manutencao", id_reator=id_reator, turno=turno, data=data)

        elif opcao == "7":
            id_reator = int(input("  ID do reator: "))
            turno     = input("  Turno (manhã/tarde/noite): ")
            tarefa    = FabricaDeTarefas.criar("gerar_relatorio", id_reator=id_reator, turno=turno)

        else:
            print("\n  Opção inválida.")
            return

        if tarefa:
            orquestrador.enfileirar(tarefa)

    except ValueError as e:
        print(f"\n  Entrada inválida: {e}")


if __name__ == "__main__":
    orquestrador = OrquestradorUsina()
    menu_principal(orquestrador)