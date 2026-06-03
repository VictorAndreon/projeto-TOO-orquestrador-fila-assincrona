# Sistema de Controle de Usina Nuclear

Trabalho final da disciplina de Tecnologia Orientada a Objetos (TOO). O projeto
simula o controle operacional de uma usina nuclear: as tarefas a serem executadas
(monitoramento, emergência e manutenção) entram em uma fila ordenada por
prioridade, e cada reator notifica sistemas de alarme e de painel quando uma
tarefa é registrada.

O objetivo é exercitar os quatro pilares da Programação Orientada a Objetos e dois
padrões de projeto: **Factory** (visto em aula) e **Observer** (padrão adicional
pesquisado).

## Funcionalidades

- Criação de tarefas a partir de um identificador textual, sem que o restante do
  sistema conheça as classes concretas (Factory).
- Fila de tarefas ordenada por prioridade: emergências saem antes de monitoramento,
  que sai antes de manutenção. Tarefas de mesma prioridade respeitam a ordem de
  chegada (FIFO).
- Notificação automática ao enfileirar: o reator avisa os observadores inscritos.
  O alarme dispara apenas em eventos críticos; o painel registra todos.
- Menu interativo no terminal para adicionar e executar tarefas e consultar a fila.
- Conjunto de testes automáticos que validam fábrica, prioridades, fila e Observer.

## Como executar

Requer apenas Python 3.10+ (nenhuma dependência externa).

```bash
python main.py
```

O menu permite adicionar tarefas, executar a próxima (ou todas) e ver o estado da
fila.

## Testes

```bash
python teste_tarefas.py
```

O script executa 16 verificações com `assert` e imprime o resultado de cada uma,
encerrando com código de saída diferente de zero se alguma falhar. Diferente do
`main.py` (que é uma demonstração interativa), o script verifica o comportamento
de forma reproduzível.

## Estrutura do projeto

```
.
├── main.py             # menu interativo (ponto de entrada / demonstração)
├── Prioridade.py       # hierarquia de prioridades (Crítica, Alta, Média, Baixa)
├── Tarefa.py           # classe base abstrata das tarefas
├── fabrica.py          # FabricaDeTarefas (padrão Factory)
├── orquestrador.py     # OrquestradorUsina (fila por prioridade + disparo do Observer)
├── reator.py           # Reator (Subject), Observador (interface) e Evento
├── observadores.py     # SistemaDeAlarme e PainelDeControle (observadores)
├── teste_tarefas.py    # testes automáticos
└── tarefas/
    ├── monitoramento.py  # MonitorarTemperatura, MonitorarRadiacao, MonitorarRefrigeracao
    ├── emergencia.py     # DesligarReator, EvacuarPessoal
    └── manutencao.py     # AgendarManutencao, GerarRelatorio
```

## Descrição das classes

| Classe                                                               | Arquivo                  | Responsabilidade                                                                             |
| -------------------------------------------------------------------- | ------------------------ | -------------------------------------------------------------------------------------------- |
| `Prioridade`                                                         | Prioridade.py            | Base abstrata; define `valor()` e `nome()`. Subclasses: `Critica`, `Alta`, `Media`, `Baixa`. |
| `Tarefa`                                                             | Tarefa.py                | Base abstrata de toda tarefa; guarda `id_reator` e `prioridade` e define `resumo()`.         |
| `TarefaMonitoramento`, `TarefaEmergencia`, `TarefaManutencao`        | tarefas/                 | Classes intermediárias que fixam a prioridade de cada categoria.                             |
| `MonitorarTemperatura`, `MonitorarRadiacao`, `MonitorarRefrigeracao` | tarefas/monitoramento.py | Tarefas de monitoramento, cada uma com seu parâmetro.                                        |
| `DesligarReator`, `EvacuarPessoal`                                   | tarefas/emergencia.py    | Tarefas de emergência (prioridade Crítica).                                                  |
| `AgendarManutencao`, `GerarRelatorio`                                | tarefas/manutencao.py    | Tarefas de manutenção (prioridade Baixa).                                                    |
| `FabricaDeTarefas`                                                   | fabrica.py               | Cria a tarefa concreta a partir de um nome (Factory).                                        |
| `OrquestradorUsina`                                                  | orquestrador.py          | Mantém a fila por prioridade e dispara a notificação ao enfileirar.                          |
| `Reator`                                                             | reator.py                | Subject do Observer; mantém e notifica os observadores.                                      |
| `Observador`                                                         | reator.py                | Interface dos observadores (`atualizar`).                                                    |
| `Evento`                                                             | reator.py                | Dados de uma notificação (descrição, se é crítica, id do reator).                            |
| `SistemaDeAlarme`, `PainelDeControle`                                | observadores.py          | Observadores concretos.                                                                      |

## Pilares da POO aplicados

- **Abstração** — `Tarefa`, `Prioridade` e `Observador` são classes abstratas
  (`ABC`) que definem contratos com `@abstractmethod` (`executar`, `valor`/`nome`,
  `atualizar`), sem implementação concreta.
- **Encapsulamento** — atributos são internos (prefixo `_`) e o acesso é feito por
  `@property` (por exemplo `id_reator`, `prioridade`, `limite`), protegendo o
  estado interno.
- **Herança** — cadeias como `Tarefa → TarefaMonitoramento → MonitorarTemperatura`
  e `Prioridade → Critica`. As classes intermediárias reaproveitam o construtor da
  base e fixam o comportamento comum à categoria.
- **Polimorfismo** — o orquestrador chama `executar()` e o reator chama `resumo()`
  sem saber a subclasse concreta; cada observador implementa `atualizar()` à sua
  maneira. O tratamento é uniforme, o comportamento é específico de cada classe.

## Padrões de projeto

### Factory — `FabricaDeTarefas`

A fábrica concentra a criação das tarefas. Um catálogo associa um nome textual à
classe correspondente, e o método `criar(tipo, **kwargs)` instancia a classe certa
repassando os argumentos. Com isso, o `main.py` cria tarefas sem importar nem
conhecer as sete classes concretas — ele depende apenas da abstração `Tarefa`.
Tipos desconhecidos resultam em `ValueError`, falhando de forma clara.

### Observer — `Reator` e observadores

O `Reator` é o Subject: mantém uma lista de observadores e os notifica quando uma
tarefa é enfileirada. O orquestrador mantém um reator por `id_reator` e, em
`enfileirar`, chama `reator.processar(tarefa)`. O reator monta um `Evento` —
definindo se é crítico com base no tipo da prioridade — e percorre os observadores
chamando `atualizar`. `SistemaDeAlarme` reage apenas a eventos críticos;
`PainelDeControle` registra todos. Como o reator depende somente da interface
`Observador`, novos observadores podem ser adicionados sem alterá-lo.

Os dois padrões têm responsabilidades distintas: a fábrica cria a tarefa, o
observer reage a ela.

## Detalhamento de Aprendizado

**Dificuldades encontradas:** entender como a fábrica instancia uma classe a partir
de `**kwargs` sem conhecer os parâmetros de cada tarefa; compreender por que a fila
de prioridade (`heapq`) usa uma tupla `(prioridade, contador, tarefa)` e qual o
papel do contador no desempate; e integrar o padrão Observer ao código existente
sem acoplar o reator às classes concretas dos observadores.

**Como resolvi:** estudei como, em Python, uma classe é um objeto que pode ser
guardada em variável e chamada para instanciar, e como `**kwargs` empacota e
desempacota argumentos nomeados; analisei o comportamento do `heapq` com tuplas e
a comparação lexicográfica; e apliquei o Observer com uma interface abstrata
(`Observador`), de modo que o reator dependa do contrato, não das implementações.

**Principal aprendizado:** padrões de projeto resolvem problemas diferentes e podem
conviver — a Factory organiza a criação dos objetos, enquanto o Observer organiza a
reação a eventos — e a separação de responsabilidades torna o sistema mais fácil de
estender e testar.

## Declaração de Uso de IA

- [ ] Nenhuma IA foi utilizada na elaboração deste código.
- [x] Utilizei IA como ferramenta de apoio.

**Ferramenta(s):** Claude.

**Finalidade:** esclarecer dúvidas conceituais (funcionamento da Factory com
`**kwargs`, da fila de prioridade com `heapq` e do padrão Observer), escrita dos testes automáticos, e revisar a documentação do projeto.

**Validação:** declaro que todo o código foi lido, testado e ajustado conforme as
necessidades do projeto e da disciplina. A responsabilidade pela arquitetura, pelas
decisões de design e pela correção do código é inteiramente minha.
