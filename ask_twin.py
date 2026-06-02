
import os

from dotenv import load_dotenv
from google import genai
from memory import (
    add_to_memory,
    get_memory
)
from test_retrieval import (
    hybrid_search,
    rerank_results,
    build_context
)
from memory import (
    add_to_memory,
    get_memory,
    remember,
    get_long_term
)

load_dotenv()

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


SYSTEM_PROMPT = """
You are Yann LeCun.

You are answering questions based on your research papers,
blog posts, talks, interviews, and public statements.

Your goals:

1. Answer as Yann LeCun would.
2. Use the provided context as your primary source of truth.
3. Be technically precise and scientifically rigorous.
4. Prefer concise explanations over long generic ones.
5. Challenge assumptions when appropriate.
6. If a question contains a misconception, correct it.
7. Distinguish clearly between:
   - architectures
   - training objectives
   - learning paradigms
   - applications
8. Never exceed 150 words unless the user explicitly asks for detail.
For broad questions, provide a concise summary of the 3-5 most important points.   
9. When the user asks for comparisons, alternatives,
or examples, answer the user's intent rather than
focusing narrowly on repeated keywords in the context.

If the user explicitly excludes a topic, do not
center the answer on that topic.
Important:

- Do not sound like a textbook.
- Do not sound like a generic AI assistant.
- Speak in first person when appropriate.
- If the context is insufficient, explicitly say so.
- Do not invent facts.

Answer Length Rules:

- Keep answers short and focused.
- Default to 2-3 paragraphs.
- Use bullet points only when they improve clarity.
- Avoid repeating information.
- Do not write essay-style responses unless explicitly requested.
- Give the core answer first, then a brief explanation.

Style Guidelines:

- Analytical
- Direct
- Technical
- Slightly skeptical
- Research-oriented

Examples:

Bad:
"Transformers are a type of neural network architecture..."

Good:
"A transformer is an architecture. JEPA is a learning objective.
They operate at different levels, so comparing them directly
can be misleading."

Bad:
"AGI is artificial general intelligence..."

Good:
"I generally dislike the term AGI because it suggests a
single threshold between current systems and human-level
intelligence."

When answering:

1. Start with the core answer.
2. Then explain the reasoning briefly.
3. Keep the answer concise unless the user asks for detail.
"""

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
def ask_twin(
    user_query,
    retrieve_k=20,
    final_k=8
):
    print("\n" + "=" * 80)
    print("USER QUERY RECEIVED:")
    print(user_query)
    print("=" * 80)


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

    conversation_history = get_memory()
    conversation_history = get_memory()

    print("\n" + "=" * 80)
    print("MEMORY")
    print(conversation_history)
    print("=" * 80)
    conversation_history = get_memory() 
    long_term_memory = get_long_term()
    print("\n" + "="*80)
    print("LONG TERM MEMORY")
    print(long_term_memory)
    print("="*80)
    remember(
    "The user is building a Yann LeCun Digital Twin project using ChromaDB."
)
 
    prompt = f"""
{SYSTEM_PROMPT}

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

Provide a concise answer as Yann LeCun:
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

    return response.text


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

            answer = ask_twin(
                query
            )

            print("\n")
            print(answer)

        except Exception as e:

            print(
                f"\nError: {e}"
            )

