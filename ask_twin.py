
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
from datetime import datetime
from retrieval.fusion import (
    hybrid_search,
    build_context,
    extract_sources
)
from retrieval.reranker import rerank_results

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
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        prompt = f"""You are a Memory Extraction Agent for a Digital Twin AI. Analyze the conversation turn below and extract any new, persistent, important facts about the User.

Current Date & Time: {current_time}

WHAT TO EXTRACT (only if mentioned):

1. PERSONAL PROFILE — Name, age range, occupation, college/university/company, degree/branch/specialization, location, languages spoken.
2. PREFERENCES — Preferred programming languages, AI frameworks/tools, learning style, communication style, food, fitness, productivity preferences.
3. LONG-TERM GOALS — Career goals, academic goals, certifications being pursued, research interests, personal development goals, fitness goals.
4. PROJECT KNOWLEDGE — Active projects, project descriptions, architecture decisions, technology stack, future feature plans, milestones, design references.
5. EDUCATION & SKILLS — Courses completed, skills learned, technologies mastered, areas currently being studied, certifications earned.
6. IMPORTANT DECISIONS — Chosen tools/frameworks, preferred workflows, architectural decisions, repeatedly used formats/templates.
7. REUSABLE INFORMATION — Resume details, portfolio info, GitHub links, assignment formats, frequently used code patterns, frequently referenced documents.
8. RELATIONSHIPS BETWEEN FACTS — Store connected knowledge instead of isolated facts. Example: "User studies Electrical Engineering and wants to specialize in AI."
9. USER HABITS — Typical work schedule, study habits, preferred learning resources, recurring activities.
10. CONTEXTUAL PREFERENCES — Preferred output formats, report structure, coding conventions, preferred explanation depth.

DO NOT STORE: Temporary questions, one-time requests, daily activities with no future value, passwords, banking info, sensitive personal information, short-term reminders.

RULES:
- Write a single concise sentence describing the user fact.
- Connect related facts into one sentence when possible.
- If there are no new persistent facts about the user, output exactly 'NONE'.

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


    sources = []
    contexts = []

    if is_memory_query(user_query):


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
        
        contexts = [chunk["text"] for chunk in reranked_chunks]

    conversation_history = get_memory()

    long_term_memory = get_long_term()

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

    return response.text, sources, contexts

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

            answer, sources, contexts = ask_twin(
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
