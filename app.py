import streamlit as st

from ask_twin import ask_twin



st.set_page_config(
    page_title="Yann LeCun Digital Twin",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Yann LeCun Digital Twin")


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )



if prompt := st.chat_input(
    "Ask Yann LeCun..."
):


    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            answer = ask_twin(
                prompt
            )

            st.markdown(
                answer
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )