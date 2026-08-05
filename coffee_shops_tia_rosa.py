"""
Sistema de gerenciamento do Coffee Shops Tia Rosa.

Funcionalidades:
- Cadastro e consulta de produtos;
- Cadastro e consulta de clientes;
- Realização de pedidos com controle de estoque;
- Programa de pontos;
- Relatório de vendas;
- Salvamento automático em arquivo JSON.

Desenvolvido para a atividade de Desenvolvimento de Sistema em Python.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List


ARQUIVO_DADOS = "dados_cafeteria.json"


@dataclass
class Produto:
    """Representa um produto vendido pela cafeteria."""

    codigo: int
    nome: str
    categoria: str
    ingredientes: str
    preco: float
    estoque: int
    desconto: float = 0.0

    def preco_final(self) -> float:
        """Retorna o preço do produto considerando o desconto cadastrado."""
        return self.preco * (1 - self.desconto / 100)


@dataclass
class Cliente:
    """Representa um cliente cadastrado no programa de fidelidade."""

    codigo: int
    nome: str
    telefone: str
    pontos: int = 0


@dataclass
class ItemPedido:
    """Representa um item incluído em um pedido."""

    codigo_produto: int
    nome_produto: str
    quantidade: int
    preco_unitario: float

    def subtotal(self) -> float:
        return self.quantidade * self.preco_unitario


@dataclass
class Pedido:
    """Representa uma venda finalizada."""

    numero: int
    data_hora: str
    codigo_cliente: int
    nome_cliente: str
    itens: List[ItemPedido]
    total: float
    pontos_gerados: int


class SistemaCafeteria:
    """Controla produtos, clientes, pedidos, estoque e relatórios."""

    def __init__(self, arquivo_dados: str = ARQUIVO_DADOS) -> None:
        self.arquivo_dados = arquivo_dados
        self.produtos: Dict[int, Produto] = {}
        self.clientes: Dict[int, Cliente] = {}
        self.pedidos: List[Pedido] = []
        self.carregar_dados()

    # ---------------------------- UTILITÁRIOS ----------------------------
    @staticmethod
    def linha() -> None:
        print("-" * 72)

    @staticmethod
    def moeda(valor: float) -> str:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def ler_inteiro(mensagem: str, minimo: int | None = None) -> int:
        while True:
            try:
                valor = int(input(mensagem).strip())
                if minimo is not None and valor < minimo:
                    print(f"Digite um valor maior ou igual a {minimo}.")
                    continue
                return valor
            except ValueError:
                print("Entrada inválida. Digite um número inteiro.")

    @staticmethod
    def ler_float(mensagem: str, minimo: float | None = None) -> float:
        while True:
            try:
                texto = input(mensagem).strip().replace(",", ".")
                valor = float(texto)
                if minimo is not None and valor < minimo:
                    print(f"Digite um valor maior ou igual a {minimo:.2f}.")
                    continue
                return valor
            except ValueError:
                print("Entrada inválida. Digite um número válido.")

    @staticmethod
    def ler_texto_obrigatorio(mensagem: str) -> str:
        while True:
            texto = input(mensagem).strip()
            if texto:
                return texto
            print("O campo não pode ficar vazio.")

    # ------------------------- PERSISTÊNCIA JSON -------------------------
    def carregar_dados(self) -> None:
        """Carrega os dados existentes ou cria um cardápio inicial."""
        if not os.path.exists(self.arquivo_dados):
            self.criar_dados_iniciais()
            return

        try:
            with open(self.arquivo_dados, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

            self.produtos = {
                int(item["codigo"]): Produto(**item) for item in dados.get("produtos", [])
            }
            self.clientes = {
                int(item["codigo"]): Cliente(**item) for item in dados.get("clientes", [])
            }

            self.pedidos = []
            for item in dados.get("pedidos", []):
                itens = [ItemPedido(**produto) for produto in item.get("itens", [])]
                self.pedidos.append(
                    Pedido(
                        numero=item["numero"],
                        data_hora=item["data_hora"],
                        codigo_cliente=item["codigo_cliente"],
                        nome_cliente=item["nome_cliente"],
                        itens=itens,
                        total=item["total"],
                        pontos_gerados=item["pontos_gerados"],
                    )
                )
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as erro:
            print(f"Aviso: não foi possível carregar os dados anteriores ({erro}).")
            print("Um novo conjunto de dados será iniciado.")
            self.produtos = {}
            self.clientes = {}
            self.pedidos = []
            self.criar_dados_iniciais()

    def salvar_dados(self) -> None:
        """Salva todos os dados do sistema em formato JSON."""
        dados = {
            "produtos": [asdict(produto) for produto in self.produtos.values()],
            "clientes": [asdict(cliente) for cliente in self.clientes.values()],
            "pedidos": [asdict(pedido) for pedido in self.pedidos],
        }
        try:
            with open(self.arquivo_dados, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=4)
        except OSError as erro:
            print(f"Não foi possível salvar os dados: {erro}")

    def criar_dados_iniciais(self) -> None:
        """Cria alguns produtos para facilitar o primeiro uso do sistema."""
        produtos_iniciais = [
            Produto(1, "Café Coado", "Bebida", "Café artesanal e água", 6.00, 30),
            Produto(2, "Cappuccino", "Bebida", "Café, leite, canela e chocolate", 12.00, 20, 10),
            Produto(3, "Pão de Queijo", "Salgado", "Polvilho, queijo, leite e ovos", 7.50, 25),
            Produto(4, "Bolo de Cenoura", "Doce", "Cenoura, farinha, ovos e chocolate", 9.00, 12),
            Produto(5, "Sanduíche Natural", "Lanche", "Pão integral, frango e salada", 15.00, 10),
        ]
        self.produtos = {produto.codigo: produto for produto in produtos_iniciais}
        self.salvar_dados()

    # ------------------------------ MENU --------------------------------
    def exibir_menu(self) -> None:
        self.linha()
        print("              COFFEE SHOPS TIA ROSA")
        print("          Sistema de Gestão da Cafeteria")
        self.linha()
        print("1 - Cadastrar produto")
        print("2 - Listar cardápio")
        print("3 - Cadastrar cliente")
        print("4 - Listar clientes")
        print("5 - Realizar pedido")
        print("6 - Consultar pedidos")
        print("7 - Relatório de vendas")
        print("0 - Encerrar o sistema")
        self.linha()

    # ---------------------------- PRODUTOS -------------------------------
    def proximo_codigo_produto(self) -> int:
        return max(self.produtos.keys(), default=0) + 1

    def cadastrar_produto(self) -> None:
        print("\nCADASTRO DE PRODUTO")
        self.linha()
        nome = self.ler_texto_obrigatorio("Nome: ")
        categoria = self.ler_texto_obrigatorio("Categoria: ")
        ingredientes = self.ler_texto_obrigatorio("Ingredientes: ")
        preco = self.ler_float("Preço: R$ ", 0.01)
        estoque = self.ler_inteiro("Quantidade em estoque: ", 0)
        desconto = self.ler_float("Desconto em porcentagem (0 a 100): ", 0)

        if desconto > 100:
            print("O desconto não pode ultrapassar 100%. Produto não cadastrado.")
            return

        codigo = self.proximo_codigo_produto()
        self.produtos[codigo] = Produto(
            codigo, nome, categoria, ingredientes, preco, estoque, desconto
        )
        self.salvar_dados()
        print(f"Produto '{nome}' cadastrado com o código {codigo}.")

    def listar_produtos(self, somente_disponiveis: bool = False) -> None:
        print("\nCARDÁPIO")
        self.linha()
        print(f"{'CÓD.':<6}{'PRODUTO':<24}{'CATEGORIA':<14}{'PREÇO':>12}{'ESTOQUE':>10}")
        self.linha()

        encontrados = 0
        for produto in sorted(self.produtos.values(), key=lambda p: p.codigo):
            if somente_disponiveis and produto.estoque <= 0:
                continue
            encontrados += 1
            promocao = " *" if produto.desconto > 0 else ""
            print(
                f"{produto.codigo:<6}{(produto.nome + promocao):<24}"
                f"{produto.categoria:<14}{self.moeda(produto.preco_final()):>12}"
                f"{produto.estoque:>10}"
            )
            print(f"      Ingredientes: {produto.ingredientes}")
            if produto.desconto > 0:
                print(
                    f"      Promoção: {produto.desconto:.0f}% de desconto "
                    f"(preço normal: {self.moeda(produto.preco)})"
                )

        if encontrados == 0:
            print("Nenhum produto disponível.")
        self.linha()
        print("* Produto em promoção")

    # ----------------------------- CLIENTES ------------------------------
    def proximo_codigo_cliente(self) -> int:
        return max(self.clientes.keys(), default=0) + 1

    def cadastrar_cliente(self) -> None:
        print("\nCADASTRO DE CLIENTE")
        self.linha()
        nome = self.ler_texto_obrigatorio("Nome: ")
        telefone = self.ler_texto_obrigatorio("Telefone: ")
        codigo = self.proximo_codigo_cliente()
        self.clientes[codigo] = Cliente(codigo, nome, telefone)
        self.salvar_dados()
        print(f"Cliente '{nome}' cadastrado com o código {codigo}.")

    def listar_clientes(self) -> None:
        print("\nCLIENTES CADASTRADOS")
        self.linha()
        if not self.clientes:
            print("Nenhum cliente cadastrado.")
            return

        print(f"{'CÓD.':<6}{'NOME':<30}{'TELEFONE':<20}{'PONTOS':>8}")
        self.linha()
        for cliente in sorted(self.clientes.values(), key=lambda c: c.codigo):
            print(
                f"{cliente.codigo:<6}{cliente.nome:<30}"
                f"{cliente.telefone:<20}{cliente.pontos:>8}"
            )
        self.linha()

    # ------------------------------ PEDIDOS ------------------------------
    def proximo_numero_pedido(self) -> int:
        return max((pedido.numero for pedido in self.pedidos), default=0) + 1

    def selecionar_cliente(self) -> Cliente | None:
        if not self.clientes:
            print("Nenhum cliente cadastrado. Cadastre um cliente antes do pedido.")
            return None

        self.listar_clientes()
        codigo = self.ler_inteiro("Código do cliente: ", 1)
        cliente = self.clientes.get(codigo)
        if cliente is None:
            print("Cliente não encontrado.")
        return cliente

    def realizar_pedido(self) -> None:
        print("\nNOVO PEDIDO")
        self.linha()
        cliente = self.selecionar_cliente()
        if cliente is None:
            return

        itens: List[ItemPedido] = []

        while True:
            self.listar_produtos(somente_disponiveis=True)
            codigo = self.ler_inteiro("Código do produto (0 para finalizar): ", 0)
            if codigo == 0:
                break

            produto = self.produtos.get(codigo)
            if produto is None:
                print("Produto não encontrado.")
                continue
            if produto.estoque <= 0:
                print("Produto sem estoque.")
                continue

            quantidade = self.ler_inteiro("Quantidade: ", 1)
            if quantidade > produto.estoque:
                print(f"Estoque insuficiente. Disponível: {produto.estoque}.")
                continue

            item_existente = next(
                (item for item in itens if item.codigo_produto == codigo), None
            )
            quantidade_ja_adicionada = item_existente.quantidade if item_existente else 0

            if quantidade + quantidade_ja_adicionada > produto.estoque:
                print("A quantidade total do item ultrapassa o estoque disponível.")
                continue

            if item_existente:
                item_existente.quantidade += quantidade
            else:
                itens.append(
                    ItemPedido(
                        produto.codigo,
                        produto.nome,
                        quantidade,
                        produto.preco_final(),
                    )
                )
            print(f"{quantidade} unidade(s) de {produto.nome} adicionada(s).")

        if not itens:
            print("Pedido cancelado: nenhum item foi selecionado.")
            return

        total = sum(item.subtotal() for item in itens)
        pontos = int(total // 10)

        print("\nRESUMO DO PEDIDO")
        self.linha()
        for item in itens:
            print(
                f"{item.quantidade}x {item.nome_produto:<30} "
                f"{self.moeda(item.subtotal()):>12}"
            )
        self.linha()
        print(f"TOTAL: {self.moeda(total)}")
        print(f"Pontos gerados: {pontos}")

        confirmar = input("Confirmar pedido? (S/N): ").strip().upper()
        if confirmar != "S":
            print("Pedido cancelado.")
            return

        for item in itens:
            self.produtos[item.codigo_produto].estoque -= item.quantidade

        cliente.pontos += pontos
        pedido = Pedido(
            numero=self.proximo_numero_pedido(),
            data_hora=datetime.now().strftime("%d/%m/%Y %H:%M"),
            codigo_cliente=cliente.codigo,
            nome_cliente=cliente.nome,
            itens=itens,
            total=round(total, 2),
            pontos_gerados=pontos,
        )
        self.pedidos.append(pedido)
        self.salvar_dados()
        print(f"Pedido nº {pedido.numero} finalizado com sucesso.")

    def listar_pedidos(self) -> None:
        print("\nPEDIDOS REALIZADOS")
        self.linha()
        if not self.pedidos:
            print("Nenhum pedido foi realizado.")
            return

        for pedido in self.pedidos:
            print(
                f"Pedido nº {pedido.numero} | {pedido.data_hora} | "
                f"Cliente: {pedido.nome_cliente}"
            )
            for item in pedido.itens:
                print(
                    f"  - {item.quantidade}x {item.nome_produto}: "
                    f"{self.moeda(item.subtotal())}"
                )
            print(
                f"  Total: {self.moeda(pedido.total)} | "
                f"Pontos: {pedido.pontos_gerados}"
            )
            self.linha()

    # ---------------------------- RELATÓRIOS -----------------------------
    def relatorio_vendas(self) -> None:
        print("\nRELATÓRIO DE VENDAS")
        self.linha()
        quantidade_pedidos = len(self.pedidos)
        total_vendido = sum(pedido.total for pedido in self.pedidos)
        ticket_medio = total_vendido / quantidade_pedidos if quantidade_pedidos else 0

        quantidades_vendidas: Dict[str, int] = {}
        for pedido in self.pedidos:
            for item in pedido.itens:
                quantidades_vendidas[item.nome_produto] = (
                    quantidades_vendidas.get(item.nome_produto, 0) + item.quantidade
                )

        produto_mais_vendido = "Nenhuma venda registrada"
        if quantidades_vendidas:
            nome, quantidade = max(quantidades_vendidas.items(), key=lambda item: item[1])
            produto_mais_vendido = f"{nome} ({quantidade} unidade(s))"

        estoque_baixo = [
            produto for produto in self.produtos.values() if produto.estoque <= 5
        ]

        print(f"Pedidos realizados: {quantidade_pedidos}")
        print(f"Total vendido: {self.moeda(total_vendido)}")
        print(f"Ticket médio: {self.moeda(ticket_medio)}")
        print(f"Clientes cadastrados: {len(self.clientes)}")
        print(f"Produto mais vendido: {produto_mais_vendido}")
        print("\nProdutos com estoque baixo (5 unidades ou menos):")
        if estoque_baixo:
            for produto in estoque_baixo:
                print(f"- {produto.nome}: {produto.estoque} unidade(s)")
        else:
            print("- Nenhum produto com estoque baixo.")
        self.linha()

    # ----------------------------- EXECUÇÃO ------------------------------
    def executar(self) -> None:
        while True:
            self.exibir_menu()
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self.cadastrar_produto()
            elif opcao == "2":
                self.listar_produtos()
            elif opcao == "3":
                self.cadastrar_cliente()
            elif opcao == "4":
                self.listar_clientes()
            elif opcao == "5":
                self.realizar_pedido()
            elif opcao == "6":
                self.listar_pedidos()
            elif opcao == "7":
                self.relatorio_vendas()
            elif opcao == "0":
                self.salvar_dados()
                print("Sistema encerrado. Até logo!")
                break
            else:
                print("Opção inválida. Escolha uma opção de 0 a 7.")

            input("\nPressione ENTER para voltar ao menu...")


def main() -> None:
    sistema = SistemaCafeteria()
    sistema.executar()


if __name__ == "__main__":
    main()
