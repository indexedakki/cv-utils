import streamlit as st
# from LangGraph import graph  
from main import graph# ✅ Import your LangGraph pipeline

st.set_page_config(page_title="CV ChatBot", layout="centered")

st.title("🧠 CV Chatbot")

# Initialize chat history in Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "semantic_results" not in st.session_state:
    st.session_state.semantic_results = None

# User input
user_input = st.chat_input("Ask me a question...")

if user_input:
    # Step 1: Prepare state for LangGraph
    state = {
        "query": user_input,
        "messages": st.session_state.messages,
        "chat_history": st.session_state.chat_history,
        "intent": "",
        "query_embedding": None,
        "semantic_results": st.session_state.semantic_results,
        "reranked_results": None,
        "final_response": None
    }

    # Step 2: Run LangGraph
    with st.spinner("Thinking..."):
        response = graph.invoke(state)

    # Step 3: Update session state
    st.session_state.chat_history = response["chat_history"]
    st.session_state.messages = response["messages"]
    st.session_state.semantic_results = response["semantic_results"]

    bot_reply = response["final_response"]

    # Step 4: Display response
    st.chat_message("user").write(user_input)
    st.chat_message("assistant").write(bot_reply)

# Display full conversation history
for user, bot in st.session_state.chat_history:
    st.chat_message("user").write(user)
    st.chat_message("assistant").write(bot)

# if st.button("🗑️ Clear Chat"):
#     st.session_state.chat_history = []
#     st.session_state.messages = []
#     st.experimental_rerun()

if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.session_state.messages = []
    st.session_state.semantic_results = None
    st.rerun()  # ✅ use this instead

