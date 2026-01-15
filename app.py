import streamlit as st
from agent import PortfolioAgent

st.set_page_config(page_title="Portfolio IA Gaspar", page_icon="🤖")

st.title("💬 Discutez avec le Portfolio de Gaspar")
st.markdown("Posez-moi des questions sur ces **projets**, ces **compétences** ou ces **expérience** chez COVEA et CPAM17 !")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es l'assistant virtuel de Gaspar. Réponds de manière professionnelle."}
    ]

agent = PortfolioAgent()


for msg in st.session_state.messages:
    if isinstance(msg, dict):
        role = msg.get("role")
        content = msg.get("content")
    else:
        role = msg.role
        content = msg.content

    if role in ["user", "assistant"] and content:
        with st.chat_message(role):
            st.markdown(content)

if prompt := st.chat_input("Ex: Quelles sont tes compétences en Python ?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Je réfléchis..."):
            try:
                response_text, updated_history = agent.get_response(st.session_state.messages)
                
                st.markdown(response_text)
                
                st.session_state.messages = updated_history
                
            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")