import sqlite3
import os


# =========================================================
# CONFIGURAÇÃO
# =========================================================

BANCO = "instance/estoque.db"


if not os.path.exists(BANCO):
    print("ERRO: estoque.db não foi encontrado.")
    print("Execute este arquivo dentro da pasta TheClosetEstoque.")
    exit()


# =========================================================
# CONEXÃO
# =========================================================

conn = sqlite3.connect(BANCO)

cursor = conn.cursor()


print("Iniciando migração do banco...")


# =========================================================
# VERIFICAR COLUNAS ATUAIS
# =========================================================

cursor.execute(
    "PRAGMA table_info(produtos)"
)

colunas = [
    coluna[1]
    for coluna in cursor.fetchall()
]


# =========================================================
# ADICIONAR NOVAS COLUNAS
# =========================================================

novas_colunas = {

    "tamanho_unico_normal":
        "INTEGER NOT NULL DEFAULT 0",

    "tamanho_p_normal":
        "INTEGER NOT NULL DEFAULT 0",

    "tamanho_m_normal":
        "INTEGER NOT NULL DEFAULT 0",

    "tamanho_g_normal":
        "INTEGER NOT NULL DEFAULT 0",

    "tamanho_gg_normal":
        "INTEGER NOT NULL DEFAULT 0",

    "tamanho_unico_promocao":
        "INTEGER NOT NULL DEFAULT 0",

    "tamanho_p_promocao":
        "INTEGER NOT NULL DEFAULT 0",

    "tamanho_m_promocao":
        "INTEGER NOT NULL DEFAULT 0",

    "tamanho_g_promocao":
        "INTEGER NOT NULL DEFAULT 0",

    "tamanho_gg_promocao":
        "INTEGER NOT NULL DEFAULT 0"
}


for nome_coluna, tipo in novas_colunas.items():

    if nome_coluna not in colunas:

        print(
            f"Criando coluna: {nome_coluna}"
        )

        cursor.execute(
            f"""
            ALTER TABLE produtos
            ADD COLUMN {nome_coluna} {tipo}
            """
        )


# =========================================================
# TRANSFERIR ESTOQUE ANTIGO
# PARA ESTOQUE NORMAL
# =========================================================

print(
    "Transferindo estoque antigo para estoque normal..."
)


cursor.execute(
    """
    UPDATE produtos
    SET
        tamanho_unico_normal = COALESCE(tamanho_unico, 0),
        tamanho_p_normal = COALESCE(tamanho_p, 0),
        tamanho_m_normal = COALESCE(tamanho_m, 0),
        tamanho_g_normal = COALESCE(tamanho_g, 0),
        tamanho_gg_normal = COALESCE(tamanho_gg, 0)
    """
)


# =========================================================
# GARANTIR PROMOÇÕES = 0
# =========================================================

cursor.execute(
    """
    UPDATE produtos
    SET
        tamanho_unico_promocao = 0,
        tamanho_p_promocao = 0,
        tamanho_m_promocao = 0,
        tamanho_g_promocao = 0,
        tamanho_gg_promocao = 0
    """
)


# =========================================================
# ADICIONAR TIPO DA VENDA
# =========================================================

cursor.execute(
    "PRAGMA table_info(vendas)"
)

colunas_vendas = [
    coluna[1]
    for coluna in cursor.fetchall()
]


if "tipo_venda" not in colunas_vendas:

    print(
        "Criando coluna tipo_venda..."
    )

    cursor.execute(
        """
        ALTER TABLE vendas
        ADD COLUMN tipo_venda
        VARCHAR(20)
        NOT NULL
        DEFAULT 'normal'
        """
    )


# =========================================================
# SALVAR
# =========================================================

conn.commit()


# =========================================================
# CONFERÊNCIA
# =========================================================

cursor.execute(
    """
    SELECT
        id,
        nome,
        tamanho_unico_normal,
        tamanho_p_normal,
        tamanho_m_normal,
        tamanho_g_normal,
        tamanho_gg_normal
    FROM produtos
    """
)


produtos = cursor.fetchall()


print()
print("=" * 60)
print("MIGRAÇÃO CONCLUÍDA")
print("=" * 60)
print()


for produto in produtos:

    (
        id_produto,
        nome,
        unico,
        p,
        m,
        g,
        gg
    ) = produto

    total = (
        unico
        + p
        + m
        + g
        + gg
    )

    print(
        f"{id_produto} - {nome}: "
        f"{total} unidade(s) no estoque normal"
    )


print()
print("=" * 60)
print("O estoque promocional foi iniciado em 0.")
print("Seus produtos antigos foram preservados.")
print("=" * 60)


conn.close()