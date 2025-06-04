import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega a chave da API
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Inicializa o modelo Gemini 1.5 Flash
model = genai.GenerativeModel("models/gemini-2.0-flash")

# Configura a interface
st.set_page_config(page_title="Data Assistant Chatbot")
st.title("🤖 Data Assistant - Chatbot para Análise de Dados")

# Histórico de conversa
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Entrada do usuário
user_input = st.chat_input("Digite sua pergunta sobre dados...")

if user_input:
    st.session_state.chat_history.append(("Usuário", user_input))

    with st.spinner("Pensando..."):
        try:
            response = model.generate_content(user_input)
            st.session_state.chat_history.append(("Assistente", response.text))
        except Exception as e:
            st.error(f"Erro ao gerar resposta: {str(e)}")

# Exibe a conversa
for speaker, text in st.session_state.chat_history:
    if speaker == "Usuário":
        st.chat_message("user").write(text)
    else:
        st.chat_message("assistant").write(text)
