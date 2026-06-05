import os
import json
from datetime import datetime

from dotenv import load_dotenv
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

from retrieval.fusion import hybrid_search, build_context, extract_sources
from retrieval.reranker import rerank_results
from eval_dataset import eval_questions
from ask_twin import ask_twin

load_dotenv(override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

def run_rag_pipeline(question, retrieve_k=20, final_k=8):

    retrieved_chunks = hybrid_search(
        question,
        top_k=retrieve_k
    )

    reranked_chunks = rerank_results(
        question,
        retrieved_chunks,
        top_k=final_k
    )

    contexts = [
        chunk["text"] for chunk in reranked_chunks
    ]

    sources = extract_sources(reranked_chunks)

    try:
        answer, _ = ask_twin(
            question,
            retrieve_k=retrieve_k,
            final_k=final_k,
            response_length="Medium"
        )
    except Exception as e:
        answer = f"Error generating response: {e}"

    return {
        "answer": answer,
        "contexts": contexts,
        "sources": sources
    }


def build_ragas_dataset(questions_list):

    data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    total = len(questions_list)

    for i, q in enumerate(questions_list):
        print(f"\n[{i+1}/{total}] Running: {q['question'][:60]}...")

        result = run_rag_pipeline(q["question"])

        data["question"].append(q["question"])
        data["answer"].append(result["answer"])
        data["contexts"].append(result["contexts"])
        data["ground_truth"].append(q["ground_truth"])

        print(f"  ✓ Got {len(result['contexts'])} contexts, answer length: {len(result['answer'])} chars")

    return Dataset.from_dict(data)


def run_evaluation():

    print("=" * 60)
    print("  RAGAS Evaluation Pipeline")
    print("  Yann LeCun Digital Twin")
    print("=" * 60)

    evaluator_llm = LangchainLLMWrapper(
        ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=API_KEY,
            temperature=0,
            max_retries=10,
        )
    )

    evaluator_embeddings = LangchainEmbeddingsWrapper(
        HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
    )

    print(f"\n📊 Running {len(eval_questions)} test queries through the RAG pipeline...\n")

    dataset = build_ragas_dataset(eval_questions)

    print(f"\n\n{'=' * 60}")
    print("  Evaluating with RAGAS metrics...")
    print("=" * 60)

    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ]
    
    answer_relevancy.strictness = 1

    results = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )

    print(f"\n\n{'=' * 60}")
    print("  📋 RAGAS EVALUATION RESULTS")
    print("=" * 60)

    df = results.to_pandas()

    for metric_name in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
        if metric_name in df.columns:
            score = float(df[metric_name].mean())
            if not str(score) == "nan":
                bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
                print(f"  {metric_name:25s}  {bar}  {score:.4f}")

    results_dict = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "num_questions": len(eval_questions),
        "scores": {},
        "per_question": []
    }

    for metric_name in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
        if metric_name in df.columns:
            score = float(df[metric_name].mean())
            if not str(score) == "nan":
                results_dict["scores"][metric_name] = round(score, 4)

    for _, row in df.iterrows():
        q_result = {
            "question": row["question"],
            "answer": row["answer"][:200] + "..." if len(str(row["answer"])) > 200 else row["answer"],
        }
        for m in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
            if m in row:
                q_result[m] = round(float(row[m]), 4) if not str(row[m]) == "nan" else None
        results_dict["per_question"].append(q_result)

    output_file = "eval_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results_dict, f, indent=2, ensure_ascii=False)

    print(f"\n  Results saved to: {output_file}")

    print(f"\n{'=' * 60}")
    print("  📊 PER-QUESTION BREAKDOWN")
    print("=" * 60)

    for i, row in df.iterrows():
        print(f"\n  Q{i+1}: {row['question'][:70]}...")
        for m in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
            if m in row and str(row[m]) != "nan":
                score = float(row[m])
                bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
                print(f"    {m:25s}  {bar}  {score:.3f}")

    print(f"\n{'=' * 60}")
    print("  Evaluation Complete!")
    print("=" * 60)

    return results


if __name__ == "__main__":
    run_evaluation()
