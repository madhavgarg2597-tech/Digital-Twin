import uuid
import sys
import os
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ask_twin import ask_twin
from eval_live import evaluate_single_turn
from memory import (
    _init_chats,
    create_chat,
    get_active_chat,
    delete_chat,
    get_memory,
    get_long_term,
    load_long_term,
    clear_long_term,
    delete_long_term_memory
)

st.set_page_config(
    page_title="Yann LeCun Digital Twin",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary: #0f0f13;
    --bg-secondary: #16161d;
    --bg-tertiary: #1c1c27;
    --bg-hover: #24243a;
    --bg-active: #2a2a45;
    --accent: #7c6aef;
    --accent-glow: rgba(124, 106, 239, 0.25);
    --accent-light: #9d8ff5;
    --text-primary: #e8e6f0;
    --text-secondary: #9896a8;
    --text-muted: #6b6980;
    --border: #2a2940;
    --border-light: #3a3955;
    --danger: #ef4444;
    --danger-hover: #dc2626;
    --success: #22c55e;
    --user-bubble: #2a2a45;
    --assistant-bubble: #1a1a2e;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.4);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.5);
    --shadow-lg: 0 8px 32px rgba(0,0,0,0.6);
    --radius: 12px;
    --radius-lg: 16px;
}

html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp > header {
    background-color: transparent !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-secondary) 0%, #111118 100%) !important;
    border-right: 1px solid var(--border) !important;
    padding-top: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] p,
[data-testid="stSidebar"] [data-testid="stMarkdown"] span,
[data-testid="stSidebar"] label {
    color: var(--text-primary) !important;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 24px 20px 20px 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
}

.sidebar-brand .brand-icon {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--accent) 0%, #5b4cc4 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 20px var(--accent-glow);
}

.sidebar-brand .brand-text {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.3px;
}

.sidebar-brand .brand-sub {
    font-size: 11px;
    color: var(--text-muted);
    letter-spacing: 0.5px;
    text-transform: uppercase;
    font-weight: 500;
}

.new-chat-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: calc(100% - 32px);
    margin: 0 16px 16px 16px;
    padding: 12px 16px;
    background: linear-gradient(135deg, var(--accent) 0%, #5b4cc4 100%);
    color: white !important;
    border: none;
    border-radius: var(--radius);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 0 20px var(--accent-glow);
    text-decoration: none;
}

.new-chat-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 0 30px var(--accent-glow), var(--shadow-md);
}

.chat-item {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    margin: 2px 10px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.15s ease;
    color: var(--text-secondary);
    font-size: 13.5px;
    gap: 10px;
    position: relative;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.chat-item:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
}

.chat-item.active {
    background: var(--bg-active);
    color: var(--text-primary);
    font-weight: 500;
    border-left: 3px solid var(--accent);
    box-shadow: inset 0 0 20px rgba(124, 106, 239, 0.08);
}

.chat-item .chat-icon {
    font-size: 16px;
    flex-shrink: 0;
}

.chat-item .chat-title {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex-grow: 1;
}

.section-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted);
    padding: 16px 20px 8px 20px;
}

.main-header {
    text-align: center;
    padding: 40px 20px 20px 20px;
}

.main-header h1 {
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent-light) 0%, var(--accent) 50%, #5b4cc4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 6px;
    letter-spacing: -0.5px;
}

.main-header .subtitle {
    color: var(--text-muted);
    font-size: 14px;
    font-weight: 400;
}

.welcome-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 20px;
    text-align: center;
}

.welcome-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent) 0%, #5b4cc4 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    margin-bottom: 24px;
    box-shadow: 0 0 40px var(--accent-glow);
    animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 40px var(--accent-glow); }
    50% { box-shadow: 0 0 60px var(--accent-glow), 0 0 80px rgba(124,106,239,0.1); }
}

.welcome-title {
    font-size: 26px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.welcome-sub {
    color: var(--text-muted);
    font-size: 15px;
    max-width: 500px;
    line-height: 1.6;
    margin-bottom: 32px;
}

.suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    max-width: 700px;
}

.suggestion-chip {
    padding: 10px 18px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 20px;
    color: var(--text-secondary);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.suggestion-chip:hover {
    background: var(--bg-hover);
    border-color: var(--accent);
    color: var(--text-primary);
    box-shadow: 0 0 15px var(--accent-glow);
}

.chat-msg {
    display: flex;
    gap: 14px;
    padding: 20px 24px;
    margin: 4px 0;
    border-radius: var(--radius);
    animation: fadeSlideIn 0.3s ease-out;
    max-width: 850px;
    margin-left: auto;
    margin-right: auto;
}

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

.chat-msg.user {
    background: var(--user-bubble);
    border: 1px solid var(--border);
}

.chat-msg.assistant {
    background: var(--assistant-bubble);
    border: 1px solid rgba(124, 106, 239, 0.1);
}

.msg-avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}

.msg-avatar.user {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.msg-avatar.assistant {
    background: linear-gradient(135deg, var(--accent) 0%, #5b4cc4 100%);
    box-shadow: 0 0 12px var(--accent-glow);
}

.msg-content {
    flex-grow: 1;
    line-height: 1.65;
    font-size: 14.5px;
    color: var(--text-primary);
    padding-top: 4px;
}

.msg-role {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.msg-role.user { color: #60a5fa; }
.msg-role.assistant { color: var(--accent-light); }

.sources-container {
    max-width: 850px;
    margin: 0 auto 8px auto;
    padding: 0 24px 0 74px;
    animation: fadeSlideIn 0.4s ease-out;
}

.sources-header {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.sources-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.source-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 20px;
    font-size: 12px;
    color: var(--text-secondary);
    transition: all 0.2s ease;
}

.source-chip:hover {
    border-color: var(--accent);
    color: var(--text-primary);
    background: var(--bg-hover);
    box-shadow: 0 0 12px var(--accent-glow);
}

.source-chip .source-icon {
    font-size: 13px;
}

.source-chip .source-title {
    max-width: 250px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.source-chip .source-year {
    color: var(--text-muted);
    font-size: 11px;
}

[data-testid="stChatInput"] {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-lg) !important;
}

[data-testid="stChatInput"] textarea {
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

.stButton > button {
    font-family: 'Inter', sans-serif !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    border: 1px solid var(--border) !important;
}

.stSpinner > div {
    border-top-color: var(--accent) !important;
}

div[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--border-light);
}

.delete-btn button {
    background: transparent !important;
    border: none !important;
    color: var(--text-muted) !important;
    padding: 4px 8px !important;
    font-size: 12px !important;
    min-height: 0 !important;
    height: auto !important;
    line-height: 1 !important;
}
.delete-btn button:hover {
    color: var(--danger) !important;
    background: rgba(239, 68, 68, 0.1) !important;
}

footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

@st.dialog("🧠 Memory Dashboard")
def memory_dashboard():
    st.markdown("### Long-Term Memory (Global)")
    st.write("Facts persistent across all chats.")
    memories = load_long_term()
    if memories:
        for i, m in enumerate(memories):
            if isinstance(m, dict):
                ts = m.get("timestamp", "unknown")
                fact = m.get("fact", "")
                
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.markdown(
                        f'<div style="background:#1c1c27;border:1px solid #2a2940;border-radius:10px;'
                        f'padding:12px 16px;margin-bottom:8px;">'
                        f'<span style="color:#6b6980;font-size:11px;">🕐 {ts}</span><br>'
                        f'<span style="color:#e0dff0;font-size:14px;">{fact}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col2:
                    st.markdown("<div style='margin-top: 15px;'>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_mem_{i}", help="Delete this memory"):
                        delete_long_term_memory(i)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write("No long-term memories saved.")
        
    if st.button("Clear Long-Term Memory", type="primary"):
        clear_long_term()
        st.rerun()
        
    st.markdown("---")
    st.markdown("### Short-Term Memory (Context Window)")
    st.write("The rolling window (last 6 messages) sent to the LLM for the current active chat.")
    st_mem = get_memory()
    if st_mem.strip():
        st.code(st_mem, language="markdown")
    else:
        st.write("No recent chat history in active chat.")

_init_chats()

with st.sidebar:

    st.markdown("""
    <div class="sidebar-brand">
        <div class="brand-icon">🧠</div>
        <div>
            <div class="brand-text">Yann LeCun</div>
            <div class="brand-sub">Digital Twin</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✨  New Chat", key="new_chat_btn", use_container_width=True, type="primary"):
        new_id = str(uuid.uuid4())[:8]
        create_chat(new_id, "New Chat")
        st.rerun()

    if st.button("🧠 View Memory", key="view_memory_btn", use_container_width=True):
        memory_dashboard()

    st.markdown('<div class="section-label">💬  Conversations</div>', unsafe_allow_html=True)

    chats = st.session_state.get("chats", {})

    if not chats:
        st.markdown(
            '<p style="color: #6b6980; font-size: 13px; padding: 8px 20px;">'
            'No conversations yet.<br>Click <b>New Chat</b> to start.</p>',
            unsafe_allow_html=True
        )

    for cid, chat_data in reversed(list(chats.items())):
        is_active = cid == st.session_state.active_chat_id
        title = chat_data.get("title", "New Chat")

        col1, col2 = st.columns([5, 1])

        with col1:
            icon = "💬" if not is_active else "▶"
            label = f"{icon}  {title}"
            if st.button(
                label,
                key=f"chat_{cid}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.active_chat_id = cid
                st.rerun()

        with col2:
            st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
            if st.button("🗑", key=f"del_{cid}", help="Delete chat"):
                delete_chat(cid)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        '<div class="section-label">📏  Response Length</div>',
        unsafe_allow_html=True
    )
    response_length = st.radio(
        "Response length",
        options=["Short", "Medium", "Detailed"],
        index=1,
        horizontal=True,
        label_visibility="collapsed",
        key="response_length"
    )

    st.markdown("---")
    st.markdown(
        '<p style="color: #6b6980; font-size: 11px; text-align: center; padding: 0 16px;">'
        'Powered by RAG • Gemini 2.5 Flash<br>'
        'Meta AI Chief Scientist Persona</p>',
        unsafe_allow_html=True
    )

active_chat = get_active_chat()

if active_chat is None:
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-avatar">🧠</div>
        <div class="welcome-title">Ask Yann LeCun Anything</div>
        <div class="welcome-sub">
            A digital twin powered by his research papers, talks, interviews,
            and public statements. Get answers the way Yann would give them —
            direct, opinionated, and technically precise.
        </div>
        <div class="suggestions">
            <div class="suggestion-chip">💡 What is JEPA?</div>
            <div class="suggestion-chip">🤖 Will LLMs lead to AGI?</div>
            <div class="suggestion-chip">🔓 Why open-source AI?</div>
            <div class="suggestion-chip">🧪 What's wrong with RL?</div>
            <div class="suggestion-chip">🌍 Is AI an existential risk?</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    chat_title = active_chat.get("title", "New Chat")
    st.markdown(f"""
    <div class="main-header">
        <h1>🧠 {chat_title}</h1>
        <div class="subtitle">Talking with Yann LeCun's Digital Twin</div>
    </div>
    """, unsafe_allow_html=True)

    messages = active_chat.get("messages", [])

    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        sources = msg.get("sources", [])

        if role == "user":
            st.markdown(f"""
            <div class="chat-msg user">
                <div class="msg-avatar user">👤</div>
                <div class="msg-content">
                    <div class="msg-role user">You</div>
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-msg assistant">
                <div class="msg-avatar assistant">🧠</div>
                <div class="msg-content">
                    <div class="msg-role assistant">Yann LeCun</div>
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if sources:
                chips = ""
                for s in sources:
                    icon = s['type_label'].split()[0] if s['type_label'] else ""
                    yr = f' <span style="color:#6b6980;font-size:11px;">({s["year"]})</span>' if s.get('year') else ""
                    chips += (
                        f'<div style="display:inline-flex;align-items:center;gap:6px;padding:6px 14px;'
                        f'background:#1c1c27;border:1px solid #2a2940;border-radius:20px;'
                        f'font-size:12px;color:#9896a8;">'
                        f'{icon} {s["title"]}{yr}</div>'
                    )
                st.markdown(
                    f'<div style="max-width:850px;margin:2px auto 12px auto;padding:0 24px 0 74px;">'
                    f'<details style="cursor:pointer;">'
                    f'<summary style="font-size:12px;font-weight:600;color:#6b6980;letter-spacing:0.5px;list-style:none;">'
                    f'📚 Sources ({len(sources)})</summary>'
                    f'<div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:8px;">'
                    f'{chips}</div></details></div>',
                    unsafe_allow_html=True
                )
            
            contexts = msg.get("contexts", [])
            # Find the user question that preceded this assistant message
            user_q = ""
            msg_index = messages.index(msg)
            if msg_index > 0 and messages[msg_index-1]["role"] == "user":
                user_q = messages[msg_index-1]["content"]

            if contexts and user_q:
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("📊 Evaluate", key=f"eval_{msg_index}"):
                        with st.spinner("Grading..."):
                            scores = evaluate_single_turn(user_q, content, contexts)
                            if "error" in scores:
                                st.error(f"Eval failed: {scores['error']}")
                            else:
                                st.success(f"**Faithfulness:** {scores['faithfulness']:.2f} | **Relevancy:** {scores['answer_relevancy']:.2f}")

    if prompt := st.chat_input("Ask Yann LeCun anything..."):

        active_chat["messages"].append({
            "role": "user",
            "content": prompt
        })

        if active_chat["title"] == "New Chat":
            title_text = prompt[:40]
            if len(prompt) > 40:
                title_text += "..."
            active_chat["title"] = title_text

        st.markdown(f"""
        <div class="chat-msg user">
            <div class="msg-avatar user">👤</div>
            <div class="msg-content">
                <div class="msg-role user">You</div>
                {prompt}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("🧠 Yann is thinking..."):
            length = st.session_state.get("response_length", "Medium")
            answer, sources, contexts = ask_twin(prompt, response_length=length)

        active_chat["messages"].append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "contexts": contexts
        })

        st.rerun()