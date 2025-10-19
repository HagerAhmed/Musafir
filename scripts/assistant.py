import os
import time
import json

from mistralai import Mistral
from mistralai.models import UserMessage
from dotenv import load_dotenv

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from minsearch_client import minsearch_index as index

from qdrant_client import QdrantClient, models


# os.environ["SSL_CERT_FILE"] = "/mnt/d/Travel Assistant/Musafir/Fortinet_CA_SSL(15).cer"
# os.environ["REQUESTS_CA_BUNDLE"] = "/mnt/d/Travel Assistant/Musafir/Fortinet_CA_SSL(15).cer"

ELASTIC_URL = os.getenv("ELASTIC_URL_LOCAL", "http://localhost:9200")
es_client = Elasticsearch(ELASTIC_URL)
print(es_client)

model = SentenceTransformer("multi-qa-distilbert-cos-v1")

load_dotenv()  
api_key = os.getenv("API_KEY")
llm_client = Mistral(api_key = api_key)

# Elasticsearch Text

def elastic_search_filter(query, city, index_name="traveller_vector"):
    
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ['city', 'section', 'subsection', 'text'],
                            "type": "best_fields"
                        }
                    }
                ]
            }
        }
    }

    # Add filter 
    if city:
        search_query["query"]["bool"]["filter"] = {
            "term": {
                "city": city
            }
        }


    response = es_client.search(index=index_name, body=search_query)
    
    result_docs = []

    for hit in response['hits']['hits']:
        result_docs.append(hit['_source'])     
    
    return result_docs

# Elasticsearch Vector
def elastic_search_hybrid(field, query, vector, city, index_name_vec="traveller_vector"):
    knn_query = {
        "field": field,
        "query_vector": vector,
        "k": 5,
        "num_candidates": 10000,
        "boost": 0.5,
        "filter": {
            "term": {
                "city": city
            }
        }
    }

    keyword_query = {
        "bool": {
            "must": {
                "multi_match": {
                    "query": query,
                    "fields": ["city^3", 'section', 'subsection', 'text'],
                    "type": "best_fields",
                    "boost": 0.5,
                }
            },
            "filter": {
                "term": {
                    "city": city
                }
            }
        }
    }

    search_query = {
        "knn": knn_query,
        "query": keyword_query,
        "size": 5,
        "_source": ["city", 'section', 'subsection', 'text', "id"]
    }

    es_results = es_client.search(
        index=index_name_vec,
        body=search_query
    )
    
    result_docs = []
    
    for hit in es_results['hits']['hits']:
        result_docs.append(hit['_source'])

    return result_docs

#Minsearch
def minsearch_search_filter(query, city):
    boost = {'text': 3.0, 'section': 0.5}
    results = index.search(
        query=query,
        filter_dict={'city': city},
        boost_dict=boost,
        num_results=5
    )
    return results

QDRANT_URL = os.getenv("QDRANT_URL")
qdrant_client = QdrantClient(url=QDRANT_URL)
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
MODEL_HANDLE = os.getenv("MODEL_HANDLE")

#Qdrant
def qdrant_rrf_search(query: str, city: str, limit: int = 5) -> list[models.ScoredPoint]:
    results = qdrant_client.query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        prefetch=[
            models.Prefetch(
                query=models.Document(
                    text=query,
                    model=MODEL_HANDLE,
                ),
                using="jina-small",
                limit=(5 * limit),
            ),
            models.Prefetch(
                query=models.Document(
                    text=query,
                    model="Qdrant/bm25",
                ),
                using="bm25",
                limit=(5 * limit),
            ),
        ],
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="city",
                    match=models.MatchValue(value=city)
                )
            ]
        ),
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        with_payload=True,
        limit=limit,  # final number of results returned
    )

    return [
    point.payload for point in results.points
]

# RAG Flow
def build_prompt(query, search_results):
    context_template = "Q: {question}\n A: {text}"

    context_parts = []
    for source in search_results:
        context_parts.append(context_template.format(question=source.get('question', ''), text=source.get('text', '')))

    context = "\n\n".join(context_parts)

    prompt_template = """
You're a travel assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}

    """.strip()
    
    prompt = prompt_template.format(question=query, context=context)

    return prompt


def llm(prompt, model_choice):
    start_time = time.time()

    # Supported Mistral models
    mistral_models = [
        "mistral-medium-2508",
        "ministral-8b-latest",
        "mistral-small-latest",
        "open-mixtral-8x7b"
   
    ]

    # Check if user-selected model is valid
    if model_choice not in mistral_models:
        raise ValueError(f"Unknown model choice: {model_choice}. Available models: {mistral_models}")

    # Call the chosen Mistral model
    response = llm_client.chat.complete(
        model=model_choice,
        messages=[UserMessage(content=prompt)],
    )

    answer = response.choices[0].message.content

    # Extract token usage (if available)
    tokens = getattr(response, "usage", None)
    token_info = {
        "prompt_tokens": getattr(tokens, "prompt_tokens", None),
        "completion_tokens": getattr(tokens, "completion_tokens", None),
        "total_tokens": getattr(tokens, "total_tokens", None),
    }

    elapsed_time = round(time.time() - start_time, 2)

    return answer, token_info, elapsed_time



def evaluate_relevance(question, answer):
    prompt_template = """
    You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
Your task is to analyze the relevance of the generated answer compared to the original answer provided.
Based on the relevance and similarity of the generated answer to the original answer, you will classify
it as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

    Here is the data for evaluation:

    Question: {question}
    Generated Answer: {answer}

    Please analyze the content and context of the generated answer in relation to the question
    and provide your evaluation in parsable JSON without using code blocks:

    {{
      "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
      "Explanation": "[Provide a brief explanation for your evaluation]"
    }}
    """.strip()

    prompt = prompt_template.format(question=question, answer=answer)
    evaluation, tokens, _ = llm(prompt, 'open-mixtral-8x7b')
    
    try:
        json_eval = json.loads(evaluation)
        return json_eval['Relevance'], json_eval['Explanation'], tokens
    except json.JSONDecodeError:
        return "UNKNOWN", "Failed to parse evaluation", tokens



def get_answer(query, city, model_choice, search_type):
    if search_type == 'Elasticsearch_Vector':
        vector = model.encode(query)
        search_results = elastic_search_hybrid("all_data_vector", query, vector, city) 
    elif search_type == 'Elasticsearch_Text':
        search_results = elastic_search_filter(query, city)
    elif search_type == "Qdrant":
        search_results = qdrant_rrf_search(query, city)
    else:
        search_type == "MinSearch"
        search_results = minsearch_search_filter(query, city)

    prompt = build_prompt(query, search_results)
    answer, tokens, response_time = llm(prompt, model_choice)
    
    relevance, explanation, eval_tokens = evaluate_relevance(query, answer)


    return {
        'answer': answer,
        'response_time': response_time,
        'relevance': relevance,
        'relevance_explanation': explanation,
        'model_used': model_choice,
        'prompt_tokens': tokens['prompt_tokens'],
        'completion_tokens': tokens['completion_tokens'],
        'total_tokens': tokens['total_tokens'],
        'eval_prompt_tokens': eval_tokens['prompt_tokens'],
        'eval_completion_tokens': eval_tokens['completion_tokens'],
        'eval_total_tokens': eval_tokens['total_tokens'],
        'search_type': search_type
    }