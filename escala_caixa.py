import json
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

st.set_page_config(
    page_title="Escala de Caixa | SFA",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

ARQUIVO_SALVO = Path("escala_salva.json")

FUNCIONARIOS = [
    "Marcelo Lico",
    "Renata",
    "Edileny",
    "Airton",
    "Arthur",
    "Marcelo Costenaro",
    "Gisele",
    "Cristiane",
    "Michele",
    "Cassio",
    "Larissa",
]

AREAS = {
    "Marcelo Lico": "Faturamento",
    "Renata": "Faturamento",
    "Michele": "Faturamento",

    "Edileny": "Créditos",
    "Marcelo Costenaro": "Créditos",
    "Cristiane": "Créditos",
    "Cassio": "Créditos",

    "Airton": "Cobrança",
    "Arthur": "Cobrança",
    "Gisele": "Cobrança",
    "Larissa": "Cobrança",
}

CORES_AREAS = {
    "Faturamento": "#00A6D6",
    "Créditos": "#92D050",
    "Cobrança": "#F47A00",
}

AZUL = "#001B49"
CINZA = "#F3F6FA"
BORDA = "#253A5F"

DIAS = [
    "SEGUNDA-FEIRA",
    "TERÇA-FEIRA",
    "QUARTA-FEIRA",
    "QUINTA-FEIRA",
    "SEXTA-FEIRA",
]

BLOCOS = {
    "MANHÃ": [
        ("Atendimento", "MANHÃ"),
        ("1º Reserva", "MANHÃ"),
        ("2º Reserva", "MANHÃ"),
    ],
    "TARDE": [
        ("Atendimento", "11:45 às 13:10"),
        ("1º Reserva", "11:45 às 13:10"),
        ("Atendimento", "PÓS INTERVALO"),
        ("1º Reserva", "PÓS INTERVALO"),
        ("2º Reserva", "PÓS INTERVALO"),
    ],
    "NOITE": [
        ("Atendimento", "17:55 às 20:00"),
        ("1º Reserva", "17:55 às 20:00"),
    ],
}


st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #F5F7FB; }
[data-testid="stSidebar"] { background: #F8FAFD; border-right: 1px solid #D6DEEA; }
.block-container { padding-top: 0.8rem; padding-bottom: 2rem; }

.main-title {
    text-align: center; color: #001B49; font-size: 42px;
    font-weight: 950; line-height: 1; margin-bottom: 4px; letter-spacing: 1px;
}
.subtitle {
    text-align: center; color: #001B49; font-size: 23px; margin-bottom: 14px;
}
.legend-wrap {
    display: flex; justify-content: center; align-items: center;
    gap: 18px; margin-bottom: 18px;
}
.legend-label { font-size: 16px; font-weight: 900; color: #001B49; }
.legend-pill {
    min-width: 135px; text-align: center; padding: 7px 18px;
    border-radius: 5px; color: #061B2E; font-weight: 900;
    box-shadow: 0 2px 6px rgba(0,0,0,.08);
}

.shift-title {
    background: linear-gradient(90deg, #001B49, #002B67);
    color: white; font-size: 30px; font-weight: 950;
    text-align: center; padding: 7px; border-radius: 3px 3px 0 0;
    margin-top: 15px; letter-spacing: 1px;
}
.scale-table {
    border-collapse: collapse; width: 100%; table-layout: fixed;
    background: white; margin-bottom: 7px; border: 1px solid #253A5F;
}
.scale-table th {
    border: 1px solid #253A5F; background: #F8FAFD; color: #001B49;
    font-weight: 950; text-align: center; padding: 6px 4px;
    font-size: 15px; line-height: 1.1;
}
.scale-table td {
    border: 1px solid #253A5F; text-align: center; padding: 0;
    height: 40px; color: #061B2E; font-weight: 750;
}
.tipo-cell, .horario-cell {
    background: #F3F6FA; color: #001B49 !important;
    font-weight: 950 !important; font-size: 15px;
}
.person-pill {
    width: 100%; height: 40px; display: flex; align-items: center;
    justify-content: center; font-weight: 850; color: #061B2E;
}
.feriado-cell {
    background: #FFD9D9; color: #7A0000; font-weight: 950;
    height: 40px; display:flex; align-items:center; justify-content:center;
}

.summary-title {
    color: #001B49; font-size: 20px; font-weight: 950;
    margin-top: 12px; margin-bottom: 6px;
}
.summary-table {
    border-collapse: collapse; width: 100%; background: white; font-size: 13px;
}
.summary-table th {
    border: 1px solid #C6D0DE; color: #001B49; background: #F8FAFD;
    padding: 7px; text-align: center; font-weight: 950;
}
.summary-table td {
    border: 1px solid #C6D0DE; padding: 7px; text-align: center; font-weight: 700;
}
.summary-name {
    text-align: left !important; color: #061B2E; font-weight: 900 !important;
}
.ok-box {
    margin-top: 14px; background: #EEF9EA; border: 1px solid #C9E8C1;
    color: #316B20; padding: 11px 14px; border-radius: 5px; font-weight: 700;
}
.alert-box {
    margin-top: 8px; background: #FFF4E5; border: 1px solid #FFD095;
    color: #7A4000; padding: 11px 14px; border-radius: 5px; font-weight: 700;
}
.sidebar-title {
    font-size: 24px; font-weight: 950; color: #001B49; margin-bottom: 16px;
}
.sidebar-section {
    font-size: 17px; font-weight: 950; color: #001B49; margin-top: 14px; margin-bottom: 8px;
}
.sidebar-card {
    background: white; border: 1px solid #D6DEEA; border-radius: 6px;
    padding: 9px; margin-bottom: 8px; color: #001B49; font-size: 12px;
}
div[data-testid="stSelectbox"] label { font-size: 0px; }
div[data-testid="stDateInput"] label, div[data-testid="stTextInput"] label {
    color: #001B49; font-weight: 800;
}
</style>
""", unsafe_allow_html=True)


def segunda_da_semana(data_base):
    return data_base - timedelta(days=data_base.weekday())


def key_slot(bloco, dia, atividade, horario):
    return f"{bloco}_{dia}_{atividade}_{horario}"


def inicializar_estado():
    if "ausencias" not in st.session_state:
        st.session_state.ausencias = []
    if "feriados" not in st.session_state:
        st.session_state.feriados = []


def pessoa_ausente(nome, data_ref, bloco):
    for a in st.session_state.ausencias:
        if a["funcionario"] != nome:
            continue
        if not (a["inicio"] <= data_ref <= a["fim"]):
            continue
        if a.get("turno", "Todos") in ["Todos", bloco]:
            return True
    return False


def data_feriado(data_ref):
    return any(f["data"] == data_ref for f in st.session_state.feriados)


def nome_feriado(data_ref):
    for f in st.session_state.feriados:
        if f["data"] == data_ref:
            return f["motivo"]
    return "Feriado"


def montar_df(datas):
    registros = []

    for bloco, linhas in BLOCOS.items():
        for atividade, horario in linhas:
            for dia, data_ref in zip(DIAS, datas):
                key = key_slot(bloco, dia, atividade, horario)
                nome = st.session_state.get(key, "—")

                if nome != "—":
                    registros.append({
                        "Bloco": bloco,
                        "Dia": dia,
                        "Data": data_ref,
                        "Atividade": atividade,
                        "Horário": horario,
                        "Funcionário": nome,
                        "Área": AREAS.get(nome, ""),
                    })

    return pd.DataFrame(registros)


def validar(df):
    alertas = []

    if df.empty:
        return alertas

    duplicados = df.groupby(["Data", "Funcionário"]).size().reset_index(name="Qtd")

    for _, row in duplicados[duplicados["Qtd"] > 1].iterrows():
        alertas.append(
            f"{row['Funcionário']} aparece {row['Qtd']} vezes em {row['Data'].strftime('%d/%m/%Y')}."
        )

    for _, row in df.iterrows():
        if pessoa_ausente(row["Funcionário"], row["Data"], row["Bloco"]):
            alertas.append(
                f"{row['Funcionário']} está escalado em {row['Data'].strftime('%d/%m/%Y')} no turno {row['Bloco']}, mas possui ausência cadastrada."
            )

        if data_feriado(row["Data"]):
            alertas.append(
                f"{row['Dia']} ({row['Data'].strftime('%d/%m/%Y')}) é feriado, mas ainda possui pessoas escaladas."
            )

    return alertas


def salvar_escala():
    dados = {
        "ausencias": [
            {
                "funcionario": a["funcionario"],
                "inicio": a["inicio"].isoformat(),
                "fim": a["fim"].isoformat(),
                "turno": a.get("turno", "Todos"),
                "motivo": a["motivo"],
            }
            for a in st.session_state.ausencias
        ],
        "feriados": [
            {
                "data": f["data"].isoformat(),
                "motivo": f["motivo"],
            }
            for f in st.session_state.feriados
        ],
        "escala": {},
    }

    for bloco, linhas in BLOCOS.items():
        for atividade, horario in linhas:
            for dia in DIAS:
                key = key_slot(bloco, dia, atividade, horario)
                dados["escala"][key] = st.session_state.get(key, "—")

    ARQUIVO_SALVO.write_text(
        json.dumps(dados, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )


def carregar_escala():
    if not ARQUIVO_SALVO.exists():
        return False

    dados = json.loads(ARQUIVO_SALVO.read_text(encoding="utf-8"))

    st.session_state.ausencias = [
        {
            "funcionario": a["funcionario"],
            "inicio": date.fromisoformat(a["inicio"]),
            "fim": date.fromisoformat(a["fim"]),
            "turno": a.get("turno", "Todos"),
            "motivo": a["motivo"],
        }
        for a in dados.get("ausencias", [])
    ]

    st.session_state.feriados = [
        {
            "data": date.fromisoformat(f["data"]),
            "motivo": f["motivo"],
        }
        for f in dados.get("feriados", [])
    ]

    for key, valor in dados.get("escala", {}).items():
        st.session_state[key] = valor

    return True


def celula_pessoa_html(nome):
    if nome == "—" or not nome:
        return ""

    area = AREAS.get(nome)
    cor = CORES_AREAS.get(area, "#E5E7EB")

    return f'<div class="person-pill" style="background:{cor};">{nome}</div>'


def tabela_bloco_html(bloco, linhas, datas):
    html = f'<div class="shift-title">{bloco}</div>'
    html += '<table class="scale-table">'
    html += "<thead><tr>"
    html += "<th style='width: 12%;'>Tipo</th>"
    html += "<th style='width: 11%;'>Horário</th>"

    for dia, data_ref in zip(DIAS, datas):
        html += f"<th>{dia}<br>{data_ref.strftime('%d/%m/%Y')}</th>"

    html += "</tr></thead><tbody>"

    for atividade, horario in linhas:
        html += "<tr>"
        html += f'<td class="tipo-cell">{atividade}</td>'
        html += f'<td class="horario-cell">{horario}</td>'

        for dia, data_ref in zip(DIAS, datas):
            key = key_slot(bloco, dia, atividade, horario)

            if data_feriado(data_ref):
                html += f'<td><div class="feriado-cell">{nome_feriado(data_ref)}</div></td>'
            else:
                nome = st.session_state.get(key, "—")
                html += f"<td>{celula_pessoa_html(nome)}</td>"

        html += "</tr>"

    html += "</tbody></table>"
    return html


def gerar_resumo_html(df):
    if df.empty:
        return "<p>Nenhum funcionário escalado ainda.</p>"

    resumo = (
        df.groupby(["Funcionário", "Área"])
        .agg(
            QT_Escala=("Funcionário", "count"),
            QT_Atendimento=("Atividade", lambda x: (x == "Atendimento").sum()),
            QT_Reserva=("Atividade", lambda x: (x != "Atendimento").sum()),
        )
        .reset_index()
        .sort_values(["Área", "Funcionário"])
    )

    metade = (len(resumo) + 1) // 2
    partes = [resumo.iloc[:metade], resumo.iloc[metade:]]

    html = '<div class="summary-title">Resumo da Semana</div>'
    html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">'

    for parte in partes:
        html += '<table class="summary-table">'
        html += """
        <thead>
            <tr>
                <th>Funcionário</th>
                <th>Área</th>
                <th>QT Escala</th>
                <th>QT Atendimento</th>
                <th>QT Reserva</th>
            </tr>
        </thead>
        <tbody>
        """

        for _, row in parte.iterrows():
            cor = CORES_AREAS.get(row["Área"], "#E5E7EB")
            html += "<tr>"
            html += f'<td class="summary-name" style="background:{cor};">{row["Funcionário"]}</td>'
            html += f'<td>{row["Área"]}</td>'
            html += f'<td>{row["QT_Escala"]}</td>'
            html += f'<td>{row["QT_Atendimento"]}</td>'
            html += f'<td>{row["QT_Reserva"]}</td>'
            html += "</tr>"

        html += "</tbody></table>"

    html += "</div>"
    return html


def desenhar_celula(ax, x, y, w, h, texto="", face="white", color="#061B2E", weight="bold", fontsize=10):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=face, edgecolor=BORDA, linewidth=0.8))
    ax.text(
        x + w / 2,
        y + h / 2,
        texto,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
        color=color,
        wrap=True,
    )


def gerar_figura_escala(datas, df):
    fig, ax = plt.subplots(figsize=(19, 10.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    semana = f"Semana de {datas[0].strftime('%d/%m/%Y')} a {datas[-1].strftime('%d/%m/%Y')}"

    ax.text(0.5, 0.972, "ESCALA DE ATENDIMENTO", ha="center", va="center", fontsize=28, fontweight="bold", color=AZUL)
    ax.text(0.5, 0.935, f"Setor Financeiro Acadêmico • {semana}", ha="center", va="center", fontsize=16, color=AZUL)

    ax.text(0.36, 0.900, "Legenda:", ha="right", va="center", fontsize=12, fontweight="bold", color=AZUL)

    legenda_x = 0.38
    for area, cor in CORES_AREAS.items():
        ax.add_patch(Rectangle((legenda_x, 0.886), 0.105, 0.028, facecolor=cor, edgecolor="none"))
        ax.text(legenda_x + 0.0525, 0.900, area, ha="center", va="center", fontsize=11, fontweight="bold", color="#061B2E")
        legenda_x += 0.14

    x0 = 0.025
    total_w = 0.95
    col_w_tipo = 0.135
    col_w_horario = 0.135
    col_w_dia = (total_w - col_w_tipo - col_w_horario) / 5

    row_h = 0.037
    header_h = 0.047
    turno_h = 0.046
    gap = 0.020

    y_top = 0.858

    for bloco, linhas in BLOCOS.items():
        tabela_h = turno_h + header_h + row_h * len(linhas)
        y_bottom = y_top - tabela_h

        ax.add_patch(Rectangle((x0, y_top - turno_h), total_w, turno_h, facecolor=AZUL, edgecolor=BORDA, linewidth=0.8))
        ax.text(x0 + total_w / 2, y_top - turno_h / 2, bloco, ha="center", va="center", fontsize=22, fontweight="bold", color="white")

        y = y_top - turno_h - header_h

        desenhar_celula(ax, x0, y, col_w_tipo, header_h, "Tipo", CINZA, AZUL, "bold", 10)
        desenhar_celula(ax, x0 + col_w_tipo, y, col_w_horario, header_h, "Horário", CINZA, AZUL, "bold", 10)

        for i, (dia, data_ref) in enumerate(zip(DIAS, datas)):
            x = x0 + col_w_tipo + col_w_horario + i * col_w_dia
            texto = f"{dia}\n{data_ref.strftime('%d/%m/%Y')}"
            desenhar_celula(ax, x, y, col_w_dia, header_h, texto, CINZA, AZUL, "bold", 9)

        for r, (atividade, horario) in enumerate(linhas):
            y_row = y - row_h * (r + 1)

            desenhar_celula(ax, x0, y_row, col_w_tipo, row_h, atividade, CINZA, AZUL, "bold", 10)
            desenhar_celula(ax, x0 + col_w_tipo, y_row, col_w_horario, row_h, horario, CINZA, AZUL, "bold", 10)

            for i, (dia, data_ref) in enumerate(zip(DIAS, datas)):
                x = x0 + col_w_tipo + col_w_horario + i * col_w_dia

                if data_feriado(data_ref):
                    texto = nome_feriado(data_ref)
                    desenhar_celula(ax, x, y_row, col_w_dia, row_h, texto, "#FFD9D9", "#7A0000", "bold", 9)
                    continue

                filtro = df[
                    (df["Data"] == data_ref)
                    & (df["Bloco"] == bloco)
                    & (df["Atividade"] == atividade)
                    & (df["Horário"] == horario)
                ]

                if filtro.empty:
                    desenhar_celula(ax, x, y_row, col_w_dia, row_h, "", "white", "#061B2E", "bold", 9)
                else:
                    nome = filtro.iloc[0]["Funcionário"]
                    area = AREAS.get(nome, "")
                    cor = CORES_AREAS.get(area, "white")
                    desenhar_celula(ax, x, y_row, col_w_dia, row_h, nome, cor, "#061B2E", "bold", 9)

        y_top = y_bottom - gap

    return fig


def exportar_png(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=220, bbox_inches="tight")
    buffer.seek(0)
    return buffer


def exportar_pdf(fig):
    buffer = BytesIO()
    with PdfPages(buffer) as pdf:
        pdf.savefig(fig, bbox_inches="tight")
    buffer.seek(0)
    return buffer


inicializar_estado()

with st.sidebar:
    st.markdown('<div class="sidebar-title">Configurações</div>', unsafe_allow_html=True)

    data_base = st.date_input("Semana de referência", value=date.today())
    segunda = segunda_da_semana(data_base)
    datas = [segunda + timedelta(days=i) for i in range(5)]

    if st.button("💾 Salvar escala", use_container_width=True):
        salvar_escala()
        st.success("Escala salva.")

    if st.button("📁 Carregar escala salva", use_container_width=True):
        if carregar_escala():
            st.success("Escala carregada.")
            st.rerun()
        else:
            st.warning("Nenhuma escala salva encontrada.")

    st.divider()

    st.markdown('<div class="sidebar-section">Ausências</div>', unsafe_allow_html=True)

    funcionario_ausente = st.selectbox("Funcionário", ["Selecione"] + FUNCIONARIOS, key="funcionario_ausente")
    inicio_ausencia = st.date_input("Início", value=segunda, key="inicio_ausencia")
    fim_ausencia = st.date_input("Fim", value=segunda, key="fim_ausencia")
    turno_ausencia = st.selectbox("Turno", ["Todos", "MANHÃ", "TARDE", "NOITE"], key="turno_ausencia")
    motivo_ausencia = st.text_input("Motivo", placeholder="Ex.: Férias, consulta...")

    if st.button("Adicionar ausência", use_container_width=True):
        if funcionario_ausente == "Selecione":
            st.error("Selecione um funcionário.")
        elif fim_ausencia < inicio_ausencia:
            st.error("A data final não pode ser anterior à inicial.")
        else:
            st.session_state.ausencias.append({
                "funcionario": funcionario_ausente,
                "inicio": inicio_ausencia,
                "fim": fim_ausencia,
                "turno": turno_ausencia,
                "motivo": motivo_ausencia or "Não informado",
            })
            st.success("Ausência adicionada.")

    if st.session_state.ausencias:
        st.caption("Ausências cadastradas")
        for a in st.session_state.ausencias:
            st.markdown(
                f"""
                <div class="sidebar-card">
                    {a["funcionario"]} | {a["inicio"].strftime("%d/%m")} a {a["fim"].strftime("%d/%m")}
                    | {a.get("turno", "Todos")} | {a["motivo"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("Limpar ausências", use_container_width=True):
            st.session_state.ausencias = []
            st.rerun()

    st.divider()

    st.markdown('<div class="sidebar-section">Feriados</div>', unsafe_allow_html=True)

    data_feriado_input = st.date_input("Data do feriado", value=segunda, key="data_feriado")
    motivo_feriado_input = st.text_input("Nome do feriado", placeholder="Feriado Municipal")

    if st.button("Adicionar feriado", use_container_width=True):
        st.session_state.feriados.append({
            "data": data_feriado_input,
            "motivo": motivo_feriado_input or "Feriado",
        })
        st.success("Feriado adicionado.")

    if st.session_state.feriados:
        st.caption("Feriados cadastrados")
        for f in st.session_state.feriados:
            st.markdown(
                f"""
                <div class="sidebar-card">
                    {f["data"].strftime("%d/%m/%Y")} | {f["motivo"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("Limpar feriados", use_container_width=True):
            st.session_state.feriados = []
            st.rerun()

    st.divider()

    if st.button("🗑️ Limpar escala", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("MANHÃ_") or key.startswith("TARDE_") or key.startswith("NOITE_"):
                del st.session_state[key]
        st.rerun()


semana_txt = f"Semana de {datas[0].strftime('%d/%m/%Y')} a {datas[-1].strftime('%d/%m/%Y')}"

st.markdown('<div class="main-title">ESCALA DE ATENDIMENTO</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">Setor Financeiro Acadêmico &nbsp;•&nbsp; {semana_txt}</div>', unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="legend-wrap">
        <div class="legend-label">Legenda:</div>
        <div class="legend-pill" style="background:{CORES_AREAS['Faturamento']}">Faturamento</div>
        <div class="legend-pill" style="background:{CORES_AREAS['Créditos']}">Créditos</div>
        <div class="legend-pill" style="background:{CORES_AREAS['Cobrança']}">Cobrança</div>
    </div>
    """,
    unsafe_allow_html=True,
)

for bloco, linhas in BLOCOS.items():
    st.markdown(tabela_bloco_html(bloco, linhas, datas), unsafe_allow_html=True)

    with st.expander(f"Editar escala — {bloco}", expanded=False):
        header = st.columns([1.1] + [1] * 5)

        with header[0]:
            st.write("")

        for col, dia, data_ref in zip(header[1:], DIAS, datas):
            with col:
                st.markdown(f"<div class='day-card'>{dia}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='day-date'>{data_ref.strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)

        for atividade, horario in linhas:
            cols = st.columns([1.1] + [1] * 5)

            with cols[0]:
                st.markdown(f"<div class='slot-title'>{atividade}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='slot-time'>{horario}</div>", unsafe_allow_html=True)

            for col, dia, data_ref in zip(cols[1:], DIAS, datas):
                with col:
                    key = key_slot(bloco, dia, atividade, horario)

                    if data_feriado(data_ref):
                        st.session_state[key] = "—"
                        st.markdown(
                            f"<div class='holiday-box'>{nome_feriado(data_ref)}</div>",
                            unsafe_allow_html=True,
                        )
                        continue

                    opcoes_validas = ["—"] + [
                        nome for nome in FUNCIONARIOS if not pessoa_ausente(nome, data_ref, bloco)
                    ]

                    atual = st.session_state.get(key, "—")

                    if atual not in opcoes_validas:
                        atual = "—"
                        st.session_state[key] = "—"

                    st.selectbox(
                        "Selecionar",
                        options=opcoes_validas,
                        index=opcoes_validas.index(atual),
                        key=key,
                    )

df = montar_df(datas)

st.markdown(gerar_resumo_html(df), unsafe_allow_html=True)

alertas = validar(df)

if alertas:
    for alerta in alertas:
        st.markdown(f"<div class='alert-box'>⚠️ {alerta}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='ok-box'>✅ Nenhuma inconsistência encontrada.</div>", unsafe_allow_html=True)

st.markdown('<div class="summary-title">Exportar escala visual</div>', unsafe_allow_html=True)

if df.empty and not st.session_state.feriados:
    st.info("Preencha a escala para liberar a exportação.")
else:
    fig = gerar_figura_escala(datas, df)
    png = exportar_png(fig)
    pdf = exportar_pdf(fig)

    col_png, col_pdf = st.columns(2)

    with col_png:
        st.download_button(
            "Baixar imagem PNG",
            data=png,
            file_name="escala_atendimento.png",
            mime="image/png",
            use_container_width=True,
        )

    with col_pdf:
        st.download_button(
            "Baixar PDF",
            data=pdf,
            file_name="escala_atendimento.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    plt.close(fig)