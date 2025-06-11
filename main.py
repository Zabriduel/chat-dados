import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
from dotenv import load_dotenv
from PIL import Image
from tabulate import tabulate

# Configuração inicial
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Prompt otimizado
SYSTEM_PROMPT = """
Você é um especialista em banco de dados. Forneça:
1. Respostas diretas e técnicas
2. Exemplos apenas quando essenciais
3. Formato conciso (máximo 3 parágrafos)
4. Destaque pontos-chave em negrito quando relevante

Regras:
- Priorize clareza sobre detalhes extensos
- Use marcadores para listas técnicas
- Limite exemplos de código a 3-5 linhas
- Responda estritamente ao questionado
"""

# Sugestões rápidas
QUICK_SUGGESTIONS = {
    "🛠️ SQL & Consultas": [
        ("Otimizar Query", "Como melhorar performance de uma query complexa com múltiplos JOINs?"),
        ("Subconsultas vs JOINs", "Quando usar subconsultas versus JOINs em SQL?"),
        ("Window Functions", "Dê exemplos práticos de uso de window functions em análise de dados"),
        ("CTEs Recursivas", "Como implementar consultas recursivas usando Common Table Expressions?")
    ],
    "📊 Modelagem de Dados": [
        ("Normalização", "Explique os níveis de normalização com exemplos práticos"),
        ("Chaves Primárias", "Como escolher entre UUID, serial ou identity para chaves primárias?"),
        ("Modelo Dimensional", "Quais as vantagens do modelo estrela para data warehouses?"),
        ("Particionamento", "Quando e como particionar tabelas em um banco de dados?")
    ],
    "⚙️ Administração": [
        ("Backup Eficiente", "Qual estratégia de backup implementar para um BD de 1TB?"),
        ("Monitoramento", "Quais métricas monitorar para garantir saúde do banco de dados?"),
        ("Escalabilidade", "Como planejar escalabilidade vertical vs horizontal para PostgreSQL?"),
        ("Tunning", "Quais parâmetros ajustar no postgresql.conf para melhor performance?")
    ],
    "🔍 Análise de Dados": [
        ("Séries Temporais", "Como analisar padrões em dados temporais com SQL?"),
        ("Análise Textual", "Quais funções usar para análise de texto em bancos de dados?"),
        ("Geoespacial", "Como trabalhar com dados geoespaciais em PostgreSQL/PostGIS?"),
        ("JSON/NoSQL", "Quando usar campos JSON em bancos relacionais?")
    ],
    "🧩 Problemas Comuns": [
        ("Deadlocks", "Como identificar e resolver deadlocks em produção?"),
        ("Bloqueios", "Estratégias para reduzir blocking em ambientes concorrentes"),
        ("Vazamento Memória", "Como diagnosticar e resolver vazamentos de memória no BD?"),
        ("Crescimento Tabelas", "O que fazer quando tabelas de log crescem descontroladamente?")
    ],
    "🔄 Migração & ETL": [
        ("Migração Schema", "Planejamento para migrar schema entre versões sem downtime"),
        ("ETL vs ELT", "Quando usar abordagem ETL versus ELT em pipelines de dados?"),
        ("CDC", "Como implementar Change Data Capture para sincronização de dados?"),
        ("Data Quality", "Quais checks implementar para garantir qualidade em processos ETL?")
    ]
}

# Configuração da página
st.set_page_config(page_title="EMS Database Assistant", page_icon="🗃️", layout="wide")
st.title("🗃️ EMS Database Assistant")

# Sidebar
with st.sidebar:
    st.header("💡 Sugestões Técnicas")
    for category, suggestions in QUICK_SUGGESTIONS.items():
        with st.expander(category, expanded=True):
            for label, suggestion in suggestions:
                if st.button(label, key=f"sug_{category}_{label}", help=suggestion, use_container_width=True):
                    st.session_state.suggestion_clicked = suggestion
                    st.rerun()

# Container fixo no topo
with st.container():
    with st.expander("📤 Enviar dados para análise", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            uploaded_file = st.file_uploader(
                "Selecione um arquivo ou imagem de schema", 
                type=["png", "jpg", "jpeg", "csv", "xlsx", "xls", "sql", "dump"],
                label_visibility="collapsed"
            )
        with col2:
            st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
            if st.button("Limpar conversa", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()

# Estado da sessão
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "suggestion_clicked" not in st.session_state:
    st.session_state.suggestion_clicked = None

# Chat container
chat_container = st.container()

# Campo de entrada
current_placeholder = "Sua pergunta sobre banco de dados..."
if st.session_state.suggestion_clicked:
    current_placeholder = st.session_state.suggestion_clicked

user_input = st.chat_input(current_placeholder)

# Processar sugestão clicada
if st.session_state.suggestion_clicked and not user_input:
    user_input = st.session_state.suggestion_clicked
    st.session_state.suggestion_clicked = None

# Processamento principal
if user_input:
    # Processar arquivo enviado
    if uploaded_file:
        try:
            if uploaded_file.type.startswith("image"):
                image = Image.open(uploaded_file)
                st.session_state.chat_history.append({"role": "user", "type": "text", "content": "Analise este diagrama de banco de dados:"})
                st.session_state.chat_history.append({"role": "user", "type": "image", "content": image})

            elif uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file, sep=None, engine="python", on_bad_lines="skip")
                preview = tabulate(df.head(10), headers="keys", tablefmt="github", showindex=False)
                st.session_state.chat_history.append({
                    "role": "user",
                    "type": "text",
                    "content": f"Analise este arquivo CSV chamado **{uploaded_file.name}**. Aqui estão as 10 primeiras linhas:\n\n```\n{preview}\n```"
                })

            elif uploaded_file.name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(uploaded_file)
                preview = tabulate(df.head(10), headers="keys", tablefmt="github", showindex=False)
                st.session_state.chat_history.append({
                    "role": "user",
                    "type": "text",
                    "content": f"Analise este arquivo Excel chamado **{uploaded_file.name}**. Aqui estão as 10 primeiras linhas:\n\n```\n{preview}\n```"
                })

            else:
                st.session_state.chat_history.append({
                    "role": "user",
                    "type": "text",
                    "content": f"Analise este arquivo {uploaded_file.type}: {uploaded_file.name}"
                })
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")
            st.session_state.chat_history.append({
                "role": "user",
                "type": "text",
                "content": f"⚠️ Erro ao processar arquivo: {str(e)}"
            })

    # Processar input de texto
    st.session_state.chat_history.append({"role": "user", "type": "text", "content": user_input})

    # Gerar resposta
    with st.spinner("Processando sua consulta..."):
        try:
            messages = [{"role": "user", "parts": [SYSTEM_PROMPT]}]
            for item in st.session_state.chat_history:
                if item["type"] == "text":
                    messages.append({"role": item["role"], "parts": [item["content"]]})
                else:
                    messages.append({"role": item["role"], "parts": [item["content"]]})

            response = model.generate_content(
                messages,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.3,
                    top_p=0.7,
                    top_k=40
                )
            )

            st.session_state.chat_history.append({
                "role": "assistant",
                "type": "text",
                "content": response.text
            })
        except Exception as e:
            st.error("Erro ao processar sua solicitação")
            st.session_state.chat_history.append({
                "role": "assistant",
                "type": "text",
                "content": f"🔍 Erro: {str(e)}. Por favor, reformule sua pergunta."
            })

    st.rerun()

# Exibir histórico
with chat_container:
    for i, item in enumerate(st.session_state.chat_history):
        if item["type"] == "text":
            with st.chat_message(item["role"]):
                st.write(item["content"])
                if item["role"] == "assistant" and i == len(st.session_state.chat_history) - 1:
                    cols = st.columns(4)
                    with cols[0]:
                        if st.button("📋 Copiar", key=f"copy_{i}"):
                            st.session_state.copied_text = item["content"]
                    with cols[1]:
                        if st.button("🔍 Detalhar", key=f"detail_{i}"):
                            st.session_state.suggestion_clicked = f"Explique em mais detalhes: {item['content'][:50]}..."
                            st.rerun()
                    with cols[2]:
                        if st.button("🔄 Reformular", key=f"rephrase_{i}"):
                            st.session_state.suggestion_clicked = f"Reformule esta resposta para um público técnico: {item['content'][:50]}..."
                            st.rerun()
                    with cols[3]:
                        if st.button("✏️ Exemplo SQL", key=f"example_{i}"):
                            st.session_state.suggestion_clicked = f"Mostre um exemplo prático em SQL para ilustrar: {item['content'][:50]}..."
                            st.rerun()
        elif item["type"] == "image":
            st.image(item["content"], caption="Diagrama enviado", use_column_width=True)
