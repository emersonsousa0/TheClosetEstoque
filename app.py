from flask import Flask, render_template, request, redirect
from datetime import datetime, date

from database.database import (
    db,
    Produto,
    Entrada,
    Venda,
    Promocao,
    PromocaoItem
)


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///estoque.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


with app.app_context():
    db.create_all()


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def home():

    # ==========================================
    # PRODUTOS
    # ==========================================

    total_produtos = Produto.query.count()


    # ==========================================
    # BUSCA TODOS OS PRODUTOS
    # ==========================================

    produtos = Produto.query.all()


    # ==========================================
    # ESTOQUE NORMAL
    # ==========================================

    total_estoque_normal = 0

    for produto in produtos:

        total_estoque_normal += (
            produto.tamanho_unico
            + produto.tamanho_p
            + produto.tamanho_m
            + produto.tamanho_g
            + produto.tamanho_gg
        )


    # ==========================================
    # ESTOQUE PROMOCIONAL
    # ==========================================

    total_estoque_promocao = 0

    for produto in produtos:

        total_estoque_promocao += (
            produto.tamanho_unico_promocao
            + produto.tamanho_p_promocao
            + produto.tamanho_m_promocao
            + produto.tamanho_g_promocao
            + produto.tamanho_gg_promocao
        )


    # ==========================================
    # ESTOQUE TOTAL
    # ==========================================

    total_estoque = (
        total_estoque_normal
        + total_estoque_promocao
    )


    # ==========================================
    # VENDAS
    # ==========================================

    total_vendas = Venda.query.count()


    # ==========================================
    # ENTRADAS
    # ==========================================

    total_entradas = Entrada.query.count()


    # ==========================================
    # DASHBOARD
    # ==========================================

    return render_template(
        "index.html",

        total_produtos=total_produtos,

        total_estoque=total_estoque,

        total_estoque_normal=total_estoque_normal,

        total_estoque_promocao=total_estoque_promocao,

        total_vendas=total_vendas,

        total_entradas=total_entradas
    )

# ============================================================
# PRODUTOS
# ============================================================

@app.route("/produtos")
def produtos():

    produtos = Produto.query.order_by(
        Produto.nome
    ).all()

    return render_template(
        "produtos.html",
        produtos=produtos
    )


@app.route("/produtos/novo", methods=["GET", "POST"])
def novo_produto():

    if request.method == "POST":

        produto = Produto(
            nome=request.form["nome"],
            categoria=request.form["categoria"],
            genero=request.form["genero"],
            preco=float(request.form["preco"]),

            tamanho_unico=int(
                request.form.get("tamanho_unico", 0)
            ),

            tamanho_p=int(
                request.form.get("tamanho_p", 0)
            ),

            tamanho_m=int(
                request.form.get("tamanho_m", 0)
            ),

            tamanho_g=int(
                request.form.get("tamanho_g", 0)
            ),

            tamanho_gg=int(
                request.form.get("tamanho_gg", 0)
            ),

            tamanho_unico_promocao=0,
            tamanho_p_promocao=0,
            tamanho_m_promocao=0,
            tamanho_g_promocao=0,
            tamanho_gg_promocao=0
        )

        db.session.add(produto)
        db.session.commit()

        return redirect("/produtos")

    return render_template(
        "novo_produto.html"
    )


@app.route("/produtos/editar/<int:id>", methods=["GET", "POST"])
def editar_produto(id):

    produto = Produto.query.get_or_404(id)

    if request.method == "POST":

        produto.nome = request.form["nome"]
        produto.categoria = request.form["categoria"]
        produto.genero = request.form["genero"]
        produto.preco = float(request.form["preco"])

        produto.tamanho_unico = int(
            request.form.get("tamanho_unico", 0)
        )

        produto.tamanho_p = int(
            request.form.get("tamanho_p", 0)
        )

        produto.tamanho_m = int(
            request.form.get("tamanho_m", 0)
        )

        produto.tamanho_g = int(
            request.form.get("tamanho_g", 0)
        )

        produto.tamanho_gg = int(
            request.form.get("tamanho_gg", 0)
        )

        db.session.commit()

        return redirect("/produtos")

    return render_template(
        "editar_produto.html",
        produto=produto
    )


@app.route("/produtos/excluir/<int:id>", methods=["POST"])
def excluir_produto(id):

    produto = Produto.query.get_or_404(id)

    db.session.delete(produto)
    db.session.commit()

    return redirect("/produtos")


# ============================================================
# ENTRADAS
# ============================================================

@app.route("/entradas")
def entradas():

    entradas = Entrada.query.order_by(
        Entrada.data.desc()
    ).all()

    return render_template(
        "entradas.html",
        entradas=entradas
    )


@app.route("/entradas/nova")
def nova_entrada():

    produtos = Produto.query.order_by(
        Produto.nome
    ).all()

    return render_template(
        "entrada_form.html",
        produtos=produtos
    )


@app.route("/entradas/nova", methods=["POST"])
def registrar_entrada():

    produto_id = request.form["produto_id"]

    produto = Produto.query.get_or_404(
        produto_id
    )

    tamanhos = {

        "Único": int(
            request.form.get("tamanho_unico", 0)
        ),

        "P": int(
            request.form.get("tamanho_p", 0)
        ),

        "M": int(
            request.form.get("tamanho_m", 0)
        ),

        "G": int(
            request.form.get("tamanho_g", 0)
        ),

        "GG": int(
            request.form.get("tamanho_gg", 0)
        )
    }

    total = sum(tamanhos.values())

    if total <= 0:

        return (
            "Informe pelo menos uma quantidade.",
            400
        )


    # Entrada sempre entra no estoque NORMAL

    if tamanhos["Único"] > 0:

        produto.tamanho_unico += tamanhos["Único"]

        db.session.add(
            Entrada(
                produto_id=produto.id,
                tamanho="Único",
                quantidade=tamanhos["Único"]
            )
        )


    if tamanhos["P"] > 0:

        produto.tamanho_p += tamanhos["P"]

        db.session.add(
            Entrada(
                produto_id=produto.id,
                tamanho="P",
                quantidade=tamanhos["P"]
            )
        )


    if tamanhos["M"] > 0:

        produto.tamanho_m += tamanhos["M"]

        db.session.add(
            Entrada(
                produto_id=produto.id,
                tamanho="M",
                quantidade=tamanhos["M"]
            )
        )


    if tamanhos["G"] > 0:

        produto.tamanho_g += tamanhos["G"]

        db.session.add(
            Entrada(
                produto_id=produto.id,
                tamanho="G",
                quantidade=tamanhos["G"]
            )
        )


    if tamanhos["GG"] > 0:

        produto.tamanho_gg += tamanhos["GG"]

        db.session.add(
            Entrada(
                produto_id=produto.id,
                tamanho="GG",
                quantidade=tamanhos["GG"]
            )
        )


    db.session.commit()

    return redirect("/entradas")


# ============================================================
# VENDAS
# ============================================================

@app.route("/vendas")
def vendas():

    vendas = Venda.query.order_by(
        Venda.data.desc()
    ).all()

    return render_template(
        "vendas.html",
        vendas=vendas
    )

@app.route("/vendas/nova")
def nova_venda():

    produtos = Produto.query.order_by(
        Produto.nome
    ).all()

    return render_template(
        "venda_form.html",
        produtos=produtos
    )
    
@app.route("/vendas/nova", methods=["POST"])
def registrar_venda():

    from datetime import date

    # =================================================
    # DADOS DO FORMULÁRIO
    # =================================================

    tipo_venda = request.form.get(
        "tipo_venda"
    )

    produto_id = request.form.get(
        "produto_id"
    )

    tamanho = request.form.get(
        "tamanho"
    )

    quantidade = int(
        request.form.get(
            "quantidade",
            0
        )
    )

    forma_pagamento = request.form.get(
        "forma_pagamento"
    )

    desconto_manual = float(
        request.form.get(
            "desconto",
            0
        )
    )

    acrescimo = float(
        request.form.get(
            "acrescimo",
            0
        )
    )


    # =================================================
    # VALIDAÇÕES BÁSICAS
    # =================================================

    if tipo_venda not in [
        "normal",
        "promocao"
    ]:

        return (
            "Tipo de venda inválido.",
            400
        )


    if not produto_id:

        return (
            "Produto não informado.",
            400
        )


    if not tamanho:

        return (
            "Tamanho não informado.",
            400
        )


    if quantidade <= 0:

        return (
            "A quantidade deve ser maior que zero.",
            400
        )


    if desconto_manual < 0:

        return (
            "O desconto não pode ser negativo.",
            400
        )


    if acrescimo < 0:

        return (
            "O acréscimo não pode ser negativo.",
            400
        )


    # =================================================
    # PRODUTO
    # =================================================

    produto = Produto.query.get_or_404(
        produto_id
    )


    # =================================================
    # PREÇO ORIGINAL
    # =================================================

    preco_original = produto.preco

    preco_unitario = preco_original


    # =================================================
    # ESTOQUE NORMAL
    # =================================================

    if tamanho == "Único":

        estoque_normal = (
            produto.tamanho_unico
        )

        estoque_promocao = (
            produto.tamanho_unico_promocao
        )


    elif tamanho == "P":

        estoque_normal = (
            produto.tamanho_p
        )

        estoque_promocao = (
            produto.tamanho_p_promocao
        )


    elif tamanho == "M":

        estoque_normal = (
            produto.tamanho_m
        )

        estoque_promocao = (
            produto.tamanho_m_promocao
        )


    elif tamanho == "G":

        estoque_normal = (
            produto.tamanho_g
        )

        estoque_promocao = (
            produto.tamanho_g_promocao
        )


    elif tamanho == "GG":

        estoque_normal = (
            produto.tamanho_gg
        )

        estoque_promocao = (
            produto.tamanho_gg_promocao
        )


    else:

        return (
            "Tamanho inválido.",
            400
        )


    # =================================================
    # VENDA NORMAL
    # =================================================

    if tipo_venda == "normal":

        # ---------------------------------------------
        # CONFERE SOMENTE O ESTOQUE NORMAL
        # ---------------------------------------------

        if quantidade > estoque_normal:

            return (
                f"Estoque normal insuficiente. "
                f"Disponível: {estoque_normal} "
                f"unidade(s).",
                400
            )


        # ---------------------------------------------
        # PREÇO NORMAL
        # ---------------------------------------------

        preco_unitario = preco_original


        # ---------------------------------------------
        # DESCONTO
        # ---------------------------------------------

        desconto_promocao = 0


        desconto_total = (
            desconto_manual
        )


        # ---------------------------------------------
        # BAIXA SOMENTE NO ESTOQUE NORMAL
        # ---------------------------------------------

        if tamanho == "Único":

            produto.tamanho_unico -= quantidade


        elif tamanho == "P":

            produto.tamanho_p -= quantidade


        elif tamanho == "M":

            produto.tamanho_m -= quantidade


        elif tamanho == "G":

            produto.tamanho_g -= quantidade


        elif tamanho == "GG":

            produto.tamanho_gg -= quantidade


    # =================================================
    # VENDA PROMOCIONAL
    # =================================================

    else:

        # ---------------------------------------------
        # CONFERE SOMENTE O ESTOQUE PROMOCIONAL
        # ---------------------------------------------

        if quantidade > estoque_promocao:

            return (
                f"Estoque promocional insuficiente. "
                f"Disponível: {estoque_promocao} "
                f"unidade(s).",
                400
            )


        # ---------------------------------------------
        # PROCURA PROMOÇÃO ATIVA
        # ---------------------------------------------

        hoje = date.today()


        promocoes = Promocao.query.filter(
            Promocao.data_inicio <= hoje,
            Promocao.data_fim >= hoje,
            Promocao.ativa == True
        ).all()


        promocao_item = None


        for promocao in promocoes:

            for item in promocao.itens:

                if (
                    item.produto_id == produto.id
                    and item.tamanho == tamanho
                    and item.quantidade > 0
                ):

                    promocao_item = item

                    break


            if promocao_item:

                break


        # ---------------------------------------------
        # PRECISA EXISTIR PROMOÇÃO
        # ---------------------------------------------

        if not promocao_item:

            return (
                "Este produto e tamanho "
                "não possuem uma promoção ativa.",
                400
            )


        # ---------------------------------------------
        # CONFERE QUANTIDADE DA PROMOÇÃO
        # ---------------------------------------------

        if quantidade > promocao_item.quantidade:

            return (
                f"A promoção possui apenas "
                f"{promocao_item.quantidade} "
                f"unidade(s) restante(s).",
                400
            )


        # ---------------------------------------------
        # PREÇO PROMOCIONAL
        # ---------------------------------------------

        preco_unitario = (
            promocao_item.preco_promocional
        )


        # ---------------------------------------------
        # DESCONTO DA PROMOÇÃO
        # ---------------------------------------------

        desconto_promocao = (
            preco_original -
            preco_unitario
        ) * quantidade


        desconto_total = (
            desconto_promocao +
            desconto_manual
        )


        # ---------------------------------------------
        # BAIXA NO ESTOQUE PROMOCIONAL
        # ---------------------------------------------

        if tamanho == "Único":

            produto.tamanho_unico_promocao -= quantidade


        elif tamanho == "P":

            produto.tamanho_p_promocao -= quantidade


        elif tamanho == "M":

            produto.tamanho_m_promocao -= quantidade


        elif tamanho == "G":

            produto.tamanho_g_promocao -= quantidade


        elif tamanho == "GG":

            produto.tamanho_gg_promocao -= quantidade


        # ---------------------------------------------
        # BAIXA NA PROMOÇÃO
        # ---------------------------------------------

        promocao_item.quantidade -= quantidade


    # =================================================
    # VALOR FINAL
    # =================================================

    subtotal = (
        preco_original *
        quantidade
    )


    valor_final = (
        subtotal
        - desconto_total
        + acrescimo
    )


    # =================================================
    # VALOR NEGATIVO
    # =================================================

    if valor_final < 0:

        db.session.rollback()

        return (
            "O valor final da venda "
            "não pode ser negativo.",
            400
        )


    # =================================================
    # REGISTRA A VENDA
    # =================================================

    venda = Venda(

        produto_id=produto.id,

        tamanho=tamanho,

        quantidade=quantidade,

        forma_pagamento=forma_pagamento,

        preco_original=preco_original,

        desconto=desconto_total,

        acrescimo=acrescimo,

        valor_final=valor_final,

        tipo_venda=tipo_venda

    )


    db.session.add(venda)


    # =================================================
    # SALVA
    # =================================================

    db.session.commit()


    return redirect("/vendas")

# ============================================================
# ESTOQUE
# ============================================================

@app.route("/estoque")
def estoque():

    produtos = Produto.query.order_by(
        Produto.nome
    ).all()

    return render_template(
        "estoque.html",
        produtos=produtos
    )


# ============================================================
# PROMOÇÕES
# ============================================================

@app.route("/promocoes")
def promocoes():

    hoje = date.today()

    promocoes = Promocao.query.order_by(
        Promocao.data_inicio.desc()
    ).all()


    for promocao in promocoes:

        if promocao.data_fim < hoje:

            promocao.ativa = False

        elif (
            promocao.data_inicio
            <= hoje
            <= promocao.data_fim
        ):

            promocao.ativa = True

        else:

            promocao.ativa = False


    db.session.commit()


    return render_template(
        "promocoes.html",
        promocoes=promocoes
    )


# ============================================================
# NOVA PROMOÇÃO
# ============================================================

@app.route("/promocoes/nova")
def nova_promocao():

    produtos = Produto.query.order_by(
        Produto.nome
    ).all()

    return render_template(
        "promocao_form.html",
        produtos=produtos
    )



@app.route("/promocoes/nova", methods=["POST"])
def criar_promocao():

    try:
        nome = request.form["nome"]

        data_inicio = datetime.strptime(
            request.form["data_inicio"],
            "%Y-%m-%d"
        ).date()

        data_fim = datetime.strptime(
            request.form["data_fim"],
            "%Y-%m-%d"
        ).date()

        if data_fim < data_inicio:
            return (
                "A data de término não pode ser "
                "anterior à data de início.",
                400
            )

        produtos_ids = request.form.getlist("produto_id[]")

        quantidades = {
            "Único": request.form.getlist("quantidade_unico[]"),
            "P": request.form.getlist("quantidade_p[]"),
            "M": request.form.getlist("quantidade_m[]"),
            "G": request.form.getlist("quantidade_g[]"),
            "GG": request.form.getlist("quantidade_gg[]")
        }

        precos_promocionais = request.form.getlist(
            "preco_promocional[]"
        )

        # Campos de estoque normal e promocional de cada tamanho
        campos_estoque = {
            "Único": (
                "tamanho_unico_normal",
                "tamanho_unico_promocao"
            ),
            "P": (
                "tamanho_p_normal",
                "tamanho_p_promocao"
            ),
            "M": (
                "tamanho_m_normal",
                "tamanho_m_promocao"
            ),
            "G": (
                "tamanho_g_normal",
                "tamanho_g_promocao"
            ),
            "GG": (
                "tamanho_gg_normal",
                "tamanho_gg_promocao"
            )
        }

        # Confere se os campos enviados pelo formulário estão completos
        if len(precos_promocionais) != len(produtos_ids):
            return "Os dados dos produtos estão incompletos.", 400

        for lista in quantidades.values():
            if len(lista) != len(produtos_ids):
                return "As quantidades dos tamanhos estão incompletas.", 400

        promocao = Promocao(
            nome=nome,
            data_inicio=data_inicio,
            data_fim=data_fim,
            ativa=True
        )

        db.session.add(promocao)
        db.session.flush()

        for indice, produto_id in enumerate(produtos_ids):

            produto = db.session.get(Produto, int(produto_id))

            if produto is None:
                db.session.rollback()
                return "Um dos produtos selecionados não foi encontrado.", 404

            preco_promocional = float(
                precos_promocionais[indice]
            )

            if preco_promocional < 0:
                db.session.rollback()
                return "O preço promocional não pode ser negativo.", 400

            for tamanho, lista in quantidades.items():

                quantidade = int(lista[indice] or 0)

                if quantidade < 0:
                    db.session.rollback()
                    return "A quantidade não pode ser negativa.", 400

                if quantidade == 0:
                    continue

                campo_normal, campo_promocao = campos_estoque[tamanho]

                estoque_normal = getattr(produto, campo_normal)

                if quantidade > estoque_normal:
                    db.session.rollback()
                    return (
                        f"Estoque normal insuficiente para "
                        f"{produto.nome}, tamanho {tamanho}. "
                        f"Disponível: {estoque_normal}.",
                        400
                    )

                # Retira do estoque normal e transfere para o promocional
                setattr(
                    produto,
                    campo_normal,
                    estoque_normal - quantidade
                )

                estoque_promocional_atual = getattr(
                    produto,
                    campo_promocao
                )

                setattr(
                    produto,
                    campo_promocao,
                    estoque_promocional_atual + quantidade
                )

                # Registra o produto e o tamanho na promoção
                item = PromocaoItem(
                    promocao_id=promocao.id,
                    produto_id=produto.id,
                    tamanho=tamanho,
                    quantidade=quantidade,
                    preco_promocional=preco_promocional
                )

                db.session.add(item)

        db.session.commit()

        return redirect("/promocoes")

    except (ValueError, TypeError):
        db.session.rollback()
        return (
            "Confira as datas, quantidades e preços informados.",
            400
        )

    except Exception:
        db.session.rollback()
        raise


# ============================================================
# EXCLUIR PROMOÇÃO
# ============================================================

@app.route("/promocoes/excluir/<int:id>", methods=["POST"])
def excluir_promocao(id):

    promocao = Promocao.query.get_or_404(id)

    # =====================================================
    # DEVOLVE OS ITENS DA PROMOÇÃO PARA O ESTOQUE NORMAL
    # =====================================================

    for item in promocao.itens:

        produto = Produto.query.get(item.produto_id)

        if not produto:
            continue

        quantidade = item.quantidade

        # -----------------------------------------------
        # ÚNICO
        # -----------------------------------------------

        if item.tamanho == "Único":

            produto.tamanho_unico_promocao -= quantidade
            produto.tamanho_unico_normal += quantidade

        # -----------------------------------------------
        # P
        # -----------------------------------------------

        elif item.tamanho == "P":

            produto.tamanho_p_promocao -= quantidade
            produto.tamanho_p_normal += quantidade

        # -----------------------------------------------
        # M
        # -----------------------------------------------

        elif item.tamanho == "M":

            produto.tamanho_m_promocao -= quantidade
            produto.tamanho_m_normal += quantidade

        # -----------------------------------------------
        # G
        # -----------------------------------------------

        elif item.tamanho == "G":

            produto.tamanho_g_promocao -= quantidade
            produto.tamanho_g_normal += quantidade

        # -----------------------------------------------
        # GG
        # -----------------------------------------------

        elif item.tamanho == "GG":

            produto.tamanho_gg_promocao -= quantidade
            produto.tamanho_gg_normal += quantidade


    # =====================================================
    # EXCLUI A PROMOÇÃO
    # =====================================================

    db.session.delete(promocao)

    db.session.commit()

    return redirect("/promocoes")
# ============================================================
# EDITAR PROMOÇÃO
# ============================================================

@app.route("/promocoes/editar/<int:id>", methods=["GET", "POST"])
def editar_promocao(id):

    promocao = Promocao.query.get_or_404(id)

    if request.method == "POST":

        # ==========================================
        # DADOS BÁSICOS
        # ==========================================

        nome = request.form["nome"]

        data_inicio = datetime.strptime(
            request.form["data_inicio"],
            "%Y-%m-%d"
        ).date()

        data_fim = datetime.strptime(
            request.form["data_fim"],
            "%Y-%m-%d"
        ).date()


        # ==========================================
        # VALIDAÇÃO DAS DATAS
        # ==========================================

        if data_fim < data_inicio:

            return (
                "A data de término não pode ser anterior "
                "à data de início.",
                400
            )


        # ==========================================
        # DADOS DOS PRODUTOS
        # ==========================================

        produtos_ids = request.form.getlist(
            "produto_id[]"
        )

        quantidades_unico = request.form.getlist(
            "quantidade_unico[]"
        )

        quantidades_p = request.form.getlist(
            "quantidade_p[]"
        )

        quantidades_m = request.form.getlist(
            "quantidade_m[]"
        )

        quantidades_g = request.form.getlist(
            "quantidade_g[]"
        )

        quantidades_gg = request.form.getlist(
            "quantidade_gg[]"
        )

        precos_promocionais = request.form.getlist(
            "preco_promocional[]"
        )


        # ==========================================
        # CONFERE AS LISTAS
        # ==========================================

        quantidade_itens = len(produtos_ids)

        if not (
            len(quantidades_unico) == quantidade_itens
            and len(quantidades_p) == quantidade_itens
            and len(quantidades_m) == quantidade_itens
            and len(quantidades_g) == quantidade_itens
            and len(quantidades_gg) == quantidade_itens
            and len(precos_promocionais) == quantidade_itens
        ):

            return (
                "Erro nos dados enviados pelo formulário.",
                400
            )


        # ==========================================
        # DEVOLVE OS ITENS ANTIGOS
        # PARA O ESTOQUE NORMAL
        # ==========================================

        itens_antigos = PromocaoItem.query.filter_by(
            promocao_id=promocao.id
        ).all()


        for item in itens_antigos:

            produto = Produto.query.get(
                item.produto_id
            )

            if not produto:
                continue


            quantidade = item.quantidade


            # --------------------------------------
            # DEVOLVE AO ESTOQUE NORMAL
            # --------------------------------------

            if item.tamanho == "Único":

                produto.tamanho_unico_normal += quantidade

                produto.tamanho_unico_promocao -= quantidade


            elif item.tamanho == "P":

                produto.tamanho_p_normal += quantidade

                produto.tamanho_p_promocao -= quantidade


            elif item.tamanho == "M":

                produto.tamanho_m_normal += quantidade

                produto.tamanho_m_promocao -= quantidade


            elif item.tamanho == "G":

                produto.tamanho_g_normal += quantidade

                produto.tamanho_g_promocao -= quantidade


            elif item.tamanho == "GG":

                produto.tamanho_gg_normal += quantidade

                produto.tamanho_gg_promocao -= quantidade


        # ==========================================
        # REMOVE OS ITENS ANTIGOS
        # ==========================================

        PromocaoItem.query.filter_by(
            promocao_id=promocao.id
        ).delete(
            synchronize_session=False
        )


        # ==========================================
        # ATUALIZA A PROMOÇÃO
        # ==========================================

        promocao.nome = nome

        promocao.data_inicio = data_inicio

        promocao.data_fim = data_fim


        # ==========================================
        # TAMANHOS
        # ==========================================

        tamanhos = [

            (
                "Único",
                quantidades_unico
            ),

            (
                "P",
                quantidades_p
            ),

            (
                "M",
                quantidades_m
            ),

            (
                "G",
                quantidades_g
            ),

            (
                "GG",
                quantidades_gg
            )

        ]


        # ==========================================
        # ADICIONA OS NOVOS ITENS
        # ==========================================

        for indice in range(quantidade_itens):

            produto_id = int(
                produtos_ids[indice]
            )

            produto = Produto.query.get(
                produto_id
            )


            if not produto:

                db.session.rollback()

                return (
                    "Produto não encontrado.",
                    400
                )


            preco_promocional = float(
                precos_promocionais[indice]
            )


            if preco_promocional < 0:

                db.session.rollback()

                return (
                    "O preço promocional não pode "
                    "ser negativo.",
                    400
                )


            # ======================================
            # CADA TAMANHO
            # ======================================

            for tamanho, lista_quantidades in tamanhos:

                quantidade = int(
                    lista_quantidades[indice]
                )


                if quantidade <= 0:
                    continue


                # ==================================
                # ESTOQUE NORMAL DISPONÍVEL
                # ==================================

                if tamanho == "Único":

                    estoque_normal = (
                        produto.tamanho_unico_normal
                    )


                elif tamanho == "P":

                    estoque_normal = (
                        produto.tamanho_p_normal
                    )


                elif tamanho == "M":

                    estoque_normal = (
                        produto.tamanho_m_normal
                    )


                elif tamanho == "G":

                    estoque_normal = (
                        produto.tamanho_g_normal
                    )


                elif tamanho == "GG":

                    estoque_normal = (
                        produto.tamanho_gg_normal
                    )


                else:

                    estoque_normal = 0


                # ==================================
                # CONFERE ESTOQUE
                # ==================================

                if quantidade > estoque_normal:

                    db.session.rollback()

                    return (
                        f"Estoque insuficiente para "
                        f"{produto.nome} - tamanho {tamanho}. "
                        f"Disponível no estoque normal: "
                        f"{estoque_normal}.",
                        400
                    )


                # ==================================
                # MOVE NORMAL → PROMOÇÃO
                # ==================================

                if tamanho == "Único":

                    produto.tamanho_unico_normal -= quantidade

                    produto.tamanho_unico_promocao += quantidade


                elif tamanho == "P":

                    produto.tamanho_p_normal -= quantidade

                    produto.tamanho_p_promocao += quantidade


                elif tamanho == "M":

                    produto.tamanho_m_normal -= quantidade

                    produto.tamanho_m_promocao += quantidade


                elif tamanho == "G":

                    produto.tamanho_g_normal -= quantidade

                    produto.tamanho_g_promocao += quantidade


                elif tamanho == "GG":

                    produto.tamanho_gg_normal -= quantidade

                    produto.tamanho_gg_promocao += quantidade


                # ==================================
                # CRIA ITEM DA PROMOÇÃO
                # ==================================

                item = PromocaoItem(

                    promocao_id=promocao.id,

                    produto_id=produto.id,

                    tamanho=tamanho,

                    quantidade=quantidade,

                    preco_promocional=preco_promocional

                )


                db.session.add(item)


        # ==========================================
        # SALVA
        # ==========================================

        db.session.commit()


        return redirect("/promocoes")


    # ==============================================
    # GET
    # ==============================================

    produtos = Produto.query.order_by(
        Produto.nome
    ).all()


    return render_template(
        "promocao_editar.html",
        promocao=promocao,
        produtos=produtos
    )

# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    app.run(debug=True)
