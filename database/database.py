from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


# =========================================================
# PRODUTO
# =========================================================

class Produto(db.Model):

    __tablename__ = "produtos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    categoria = db.Column(
        db.String(50),
        nullable=False
    )

    genero = db.Column(
        db.String(20),
        nullable=False
    )

    preco = db.Column(
        db.Float,
        nullable=False
    )


    # =====================================================
    # ESTOQUE NORMAL
    # =====================================================

    tamanho_unico_normal = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    tamanho_p_normal = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    tamanho_m_normal = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    tamanho_g_normal = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    tamanho_gg_normal = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )


    # =====================================================
    # ESTOQUE EM PROMOÇÃO
    # =====================================================

    tamanho_unico_promocao = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    tamanho_p_promocao = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    tamanho_m_promocao = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    tamanho_g_promocao = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    tamanho_gg_promocao = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )


    # =====================================================
    # ESTOQUE TOTAL POR TAMANHO
    # =====================================================

    @property
    def tamanho_unico(self):

        return (
            self.tamanho_unico_normal
            + self.tamanho_unico_promocao
        )


    @property
    def tamanho_p(self):

        return (
            self.tamanho_p_normal
            + self.tamanho_p_promocao
        )


    @property
    def tamanho_m(self):

        return (
            self.tamanho_m_normal
            + self.tamanho_m_promocao
        )


    @property
    def tamanho_g(self):

        return (
            self.tamanho_g_normal
            + self.tamanho_g_promocao
        )


    @property
    def tamanho_gg(self):

        return (
            self.tamanho_gg_normal
            + self.tamanho_gg_promocao
        )


    # =====================================================
    # ESTOQUE NORMAL TOTAL
    # =====================================================

    def estoque_normal_total(self):

        return (
            self.tamanho_unico_normal
            + self.tamanho_p_normal
            + self.tamanho_m_normal
            + self.tamanho_g_normal
            + self.tamanho_gg_normal
        )


    # =====================================================
    # ESTOQUE EM PROMOÇÃO TOTAL
    # =====================================================

    def estoque_promocao_total(self):

        return (
            self.tamanho_unico_promocao
            + self.tamanho_p_promocao
            + self.tamanho_m_promocao
            + self.tamanho_g_promocao
            + self.tamanho_gg_promocao
        )


    # =====================================================
    # ESTOQUE TOTAL
    # =====================================================

    def estoque_total(self):

        return (
            self.estoque_normal_total()
            + self.estoque_promocao_total()
        )


    # =====================================================
    # ESTOQUE NORMAL POR TAMANHO
    # =====================================================

    def estoque_normal_por_tamanho(self, tamanho):

        if tamanho == "Único":
            return self.tamanho_unico_normal

        elif tamanho == "P":
            return self.tamanho_p_normal

        elif tamanho == "M":
            return self.tamanho_m_normal

        elif tamanho == "G":
            return self.tamanho_g_normal

        elif tamanho == "GG":
            return self.tamanho_gg_normal

        return 0


    # =====================================================
    # ESTOQUE PROMOCIONAL POR TAMANHO
    # =====================================================

    def estoque_promocao_por_tamanho(self, tamanho):

        if tamanho == "Único":
            return self.tamanho_unico_promocao

        elif tamanho == "P":
            return self.tamanho_p_promocao

        elif tamanho == "M":
            return self.tamanho_m_promocao

        elif tamanho == "G":
            return self.tamanho_g_promocao

        elif tamanho == "GG":
            return self.tamanho_gg_promocao

        return 0


# =========================================================
# ENTRADA
# =========================================================

class Entrada(db.Model):

    __tablename__ = "entradas"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    produto_id = db.Column(
        db.Integer,
        db.ForeignKey("produtos.id"),
        nullable=False
    )

    tamanho = db.Column(
        db.String(10),
        nullable=False
    )

    quantidade = db.Column(
        db.Integer,
        nullable=False
    )

    data = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()
    )


    produto = db.relationship(
        "Produto",
        backref=db.backref(
            "entradas",
            lazy=True
        )
    )


# =========================================================
# VENDA
# =========================================================

class Venda(db.Model):

    __tablename__ = "vendas"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    produto_id = db.Column(
        db.Integer,
        db.ForeignKey("produtos.id"),
        nullable=False
    )

    tamanho = db.Column(
        db.String(10),
        nullable=False
    )

    quantidade = db.Column(
        db.Integer,
        nullable=False
    )

    # =====================================================
    # TIPO DA VENDA
    # normal ou promocao
    # =====================================================

    tipo_venda = db.Column(
        db.String(20),
        nullable=False,
        default="normal"
    )

    forma_pagamento = db.Column(
        db.String(20),
        nullable=False
    )

    preco_original = db.Column(
        db.Float,
        nullable=False
    )

    desconto = db.Column(
        db.Float,
        default=0
    )

    acrescimo = db.Column(
        db.Float,
        default=0
    )

    valor_final = db.Column(
        db.Float,
        nullable=False
    )

    data = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()
    )


    produto = db.relationship(
        "Produto",
        backref=db.backref(
            "vendas",
            lazy=True
        )
    )


# =========================================================
# PROMOÇÃO
# =========================================================

class Promocao(db.Model):

    __tablename__ = "promocoes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    data_inicio = db.Column(
        db.Date,
        nullable=False
    )

    data_fim = db.Column(
        db.Date,
        nullable=False
    )

    ativa = db.Column(
        db.Boolean,
        default=True
    )


    itens = db.relationship(
        "PromocaoItem",
        backref="promocao",
        lazy=True,
        cascade="all, delete-orphan"
    )


# =========================================================
# ITEM DA PROMOÇÃO
# =========================================================

class PromocaoItem(db.Model):

    __tablename__ = "promocao_itens"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    promocao_id = db.Column(
        db.Integer,
        db.ForeignKey("promocoes.id"),
        nullable=False
    )

    produto_id = db.Column(
        db.Integer,
        db.ForeignKey("produtos.id"),
        nullable=False
    )

    tamanho = db.Column(
        db.String(10),
        nullable=False
    )

    quantidade = db.Column(
        db.Integer,
        nullable=False
    )

    preco_promocional = db.Column(
        db.Float,
        nullable=False
    )


    produto = db.relationship(
        "Produto",
        backref=db.backref(
            "promocoes",
            lazy=True
        )
    )