import streamlit as st
import uuid
import json
import os
from upstash_redis import Redis
from dotenv import load_dotenv
from agent import PortfolioAgent

load_dotenv()

st.set_page_config(
    page_title="Portfolio IA Gaspar",
    page_icon="🤖",
    layout="centered"
)

st.title("💬 Discutez avec le Portfolio de Gaspar")
st.markdown("Posez-moi des questions sur **ses** projets, **ses** compétences ou **son** expérience !")

try:
    redis = Redis(
        url=os.getenv("UPSTASH_REDIS_REST_URL"),
        token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
    )
except Exception:
    redis = None

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def serialize_message(msg):
    """Convertit les objets complexes en dictionnaire pour JSON/Redis"""
    if isinstance(msg, dict):
        return msg
    else:
        return {
            "role": msg.role,
            "content": msg.content if msg.content else ""
        }

def save_to_redis(history):
    """Sauvegarde l'historique dans le Cloud"""
    if redis:
        try:
            clean_history = [serialize_message(m) for m in history]
            redis.set(f"chat:{st.session_state.session_id}", json.dumps(clean_history), ex=86400)
        except Exception as e:
            print(f"Erreur Redis : {e}")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es l'assistant virtuel de Gaspar. Réponds de manière professionnelle."}
    ]

if "agent" not in st.session_state:
    st.session_state.agent = PortfolioAgent()

chat_container = st.container(height=500)

with chat_container:
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

if prompt := st.chat_input("Votre question..."):  
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("Je réfléchis..."):
                try:
                    response_text, updated_history = st.session_state.agent.get_response(st.session_state.messages)    
                    st.markdown(response_text)
                    updated_history.append({"role": "assistant", "content": response_text})
                    st.session_state.messages = updated_history
                    save_to_redis(updated_history)
                    
                except Exception as e:
                    st.error(f"Une erreur est survenue : {e}")