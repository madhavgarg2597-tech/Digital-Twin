import os
from dotenv import load_dotenv
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv(override=True)

def evaluate_single_turn(question, answer, contexts):
    """
    Evaluates a single chat turn dynamically using RAGAS without needing a ground_truth.
    """
    
    if not contexts:
        return {"faithfulness": 0.0, "answer_relevancy": 0.0, "error": "No contexts retrieved."}

    data = {
        "question": [question],
        "answer": [answer],
        "contexts": [contexts]
    }
    dataset = Dataset.from_dict(data)

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        return {"error": "GROQ_API_KEY is not set."}

    try:
        evaluator_llm = LangchainLLMWrapper(
            ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=groq_api_key,
            )
        )

        evaluator_embeddings = LangchainEmbeddingsWrapper(
            HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        )

        metrics = [faithfulness, answer_relevancy]
        answer_relevancy.strictness = 1

        results = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=evaluator_llm,
            embeddings=evaluator_embeddings,
        )
        f_score = results["faithfulness"]
        if isinstance(f_score, list):
            f_score = f_score[0]
            
        a_score = results["answer_relevancy"]
        if isinstance(a_score, list):
            a_score = a_score[0]
            
        return {
            "faithfulness": float(f_score),
            "answer_relevancy": float(a_score)
        }
    except Exception as e:
        import traceback
        return {"error": f"{str(e)} | Traceback: {traceback.format_exc()}"}
