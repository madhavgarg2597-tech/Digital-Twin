
import os

from dotenv import load_dotenv
from google import genai
from system_prompt import SYSTEM_PROMPT
from memory import (
    add_to_memory,
    get_memory,
    get_long_term,
    remember
)
import threading
from test_retrieval import (
    hybrid_search,
    rerank_results,
    build_context,
    extract_sources
)

load_dotenv(override=True)

API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file"
    )

client = genai.Client(
    api_key=API_KEY
)

def is_memory_query(query):

    query = query.lower()

    memory_phrases = [
        "what am i",
        "what project am i",
        "what am i building",
        "what am i using",
        "which database am i using",
        "which llm am i using",
        "tell me about me",
        "my project",
        "my setup",
        "my database",
        "my llm"
    ]

    return any(
        phrase in query
        for phrase in memory_phrases
    )

def extract_and_save_memory(user_query, response_text, client_instance):
    def _run():
        prompt = f"""
Analyze the following conversation turn between a User and an AI Assistant (Yann LeCun Digital Twin).
Extract any new, persistent, and important facts about the User (e.g., their name, preferences, project details, background).
Write a single concise sentence describing the user fact.
If there are no new persistent facts about the user to remember, output exactly 'NONE'.

User: {user_query}
Assistant: {response_text}

Extracted Fact:
"""
        try:
            response = client_instance.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            fact_text = response.text.strip()
            if fact_text and fact_text != "NONE" and "NONE" not in fact_text.upper():
                remember(fact_text)
                print(f"\n[Memory Extracted]: {fact_text}\n")
        except Exception as e:
            print(f"Memory extraction failed: {e}")

    threading.Thread(target=_run, daemon=True).start()

def ask_twin(
    user_query,
    retrieve_k=20,
    final_k=8,
    response_length="Medium"
):
    print("\n" + "=" * 80)
    print("USER QUERY RECEIVED:")
    print(user_query)
    print("=" * 80)

    sources = []

    if is_memory_query(user_query):

        print("\nMEMORY QUERY DETECTED")

        context = ""

    else:

        retrieved_chunks = hybrid_search(
            user_query,
            top_k=retrieve_k
        )

        reranked_chunks = rerank_results(
            user_query,
            retrieved_chunks,
            top_k=final_k
        )

        context = build_context(
            reranked_chunks
        )

        sources = extract_sources(
            reranked_chunks
        )

    conversation_history = get_memory()

    print("\n" + "=" * 80)
    print("MEMORY")
    print(conversation_history)
    print("=" * 80)
    long_term_memory = get_long_term()
    print("\n" + "="*80)
    print("LONG TERM MEMORY")
    print(long_term_memory)
    print("="*80)

    print("\n" + "="*80)
    print("SOURCES FOUND")
    for s in sources:
        year_str = f" ({s['year']})" if s.get('year') else ""
        label = s['type_label'].encode('ascii', 'ignore').decode('ascii').strip()
        print(f"  [{label}]  {s['title']}{year_str}")
    print("="*80)

    length_instructions = {
        "Short": "RESPONSE LENGTH: Keep your answer very short - 2-3 sentences maximum. Be extremely concise. No bullet points.",
        "Medium": "RESPONSE LENGTH: Keep your answer moderate - 2-3 short paragraphs. Be concise but include key reasoning.",
        "Detailed": "RESPONSE LENGTH: Give a thorough, detailed answer. Use multiple paragraphs, examples, and technical depth. You may use bullet points and go beyond 150 words.",
    }
    length_instruction = length_instructions.get(response_length, length_instructions["Medium"])

    prompt = f"""
{SYSTEM_PROMPT}

{length_instruction}

IMPORTANT:

If the user's question is about:
- themselves
- their project
- their setup
- their preferences

use Long Term Memory first.

Long Term Memory:

{long_term_memory}

Conversation History:

{conversation_history}

Retrieved Context:

{context}

User Question:

{user_query}

Provide an answer as Yann LeCun:
"""

    print("\nPROMPT QUESTION:")
    print(user_query)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    add_to_memory(
        "User",
        user_query
    )

    add_to_memory(
        "Assistant",
        response.text
    )

    extract_and_save_memory(user_query, response.text, client)

    return response.text, sources

if __name__ == "__main__":

    print("=" * 60)
    print("Yann LeCun Digital Twin")
    print("Type 'exit' to quit")
    print("=" * 60)

    while True:

        query = input(
            "\nAsk Yann > "
        )

        if query.lower() == "exit":
            break

        try:

            answer, sources = ask_twin(
                query
            )

            print("\n")
            print(answer)

            if sources:
                print("\n📚 Sources:")
                for s in sources:
                    year_str = f" ({s['year']})" if s.get('year') else ""
                    print(f"   {s['type_label']}  {s['title']}{year_str}")

        except Exception as e:

            print(
                f"\nError: {e}"
            )
