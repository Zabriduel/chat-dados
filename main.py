import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image

# Configuração inicial
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Prompt do sistema
SYSTEM_PROMPT = """..."""  # Mantém o mesmo prompt anterior

st.set_page_config(page_title="EMS Assistente de Dados", page_icon="📊")
st.title("📊 EMS Assistente de Dados")

# Inicialização do estado da sessão
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_uploaded" not in st.session_state:
    st.session_state.last_uploaded = None

# Função para exibir histórico
def display_history():
    for role, message in st.session_state.chat_history:
        if isinstance(message, str):
            st.chat_message(role).write(message)
        else:
            st.chat_message(role).image(message, caption="Gráfico enviado")

# Upload de arquivo com controle
uploaded_file = st.file_uploader("Envie um gráfico para análise", 
                                type=["png", "jpg", "jpeg"],
                                key="file_uploader")

# Processamento da entrada do usuário
user_input = st.chat_input("Sua dúvida sobre dados ou gráficos?")

if uploaded_file and uploaded_file != st.session_state.last_uploaded:
    # Novo arquivo detectado
    st.session_state.last_uploaded = uploaded_file
    image = Image.open(uploaded_file)
    st.session_state.chat_history.append(("user", image))
    display_history()
    st.rerun()

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    display_history()
    
    with st.spinner("Analisando..."):
        try:
            # Prepara o contexto evitando duplicação
            messages = []
            for i, (role, content) in enumerate(st.session_state.chat_history):
                if i == len(st.session_state.chat_history)-1 and user_input:
                    continue  # Evita duplicar a última mensagem
                
                if isinstance(content, str):
                    messages.append({"role": role, "parts": [content]})
                else:
                    messages.append({"role": role, "parts": [content]})
            
            if user_input:
                messages.append({"role": "user", "parts": [user_input]})
            
            response = model.generate_content(messages)
            st.session_state.chat_history.append(("assistant", response.text))
            st.rerun()
            
        except Exception as e:
            st.session_state.chat_history.append(("assistant", 
                "🔍 Erro na análise. Por favor, reformule ou envie a imagem novamente."))
            st.rerun()

# Exibe o histórico após processamento
display_history()