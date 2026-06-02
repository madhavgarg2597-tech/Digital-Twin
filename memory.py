import json
from pathlib import Path

import streamlit as st


if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []

def add_to_memory(role, content):

    st.session_state.chat_memory.append({
        "role": role,
        "content": content
    })

    st.session_state.chat_memory = (
        st.session_state.chat_memory[-6:]
    )

def get_memory():

    history = []

    for item in st.session_state.chat_memory:

        history.append(
            f"{item['role']}: {item['content']}"
        )

    return "\n".join(history)

def clear_memory():

    st.session_state.chat_memory = []


MEMORY_FILE = "long_term_memory.json"

def load_long_term():

    if not Path(MEMORY_FILE).exists():

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump([], f)

        return []

    with open(
        MEMORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

def save_long_term(memories):

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memories,
            f,
            indent=2,
            ensure_ascii=False
        )

def remember(memory_text):

    memories = load_long_term()

    if memory_text not in memories:

        memories.append(
            memory_text
        )

        save_long_term(
            memories
        )

def get_long_term():

    memories = load_long_term()

    return "\n".join(memories)

def clear_long_term():

    save_long_term([])