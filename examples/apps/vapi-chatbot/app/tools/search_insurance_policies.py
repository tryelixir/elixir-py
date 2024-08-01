from pinecone import Pinecone
import openai
import os
from openai.types.chat import ChatCompletionToolParam
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "insurance-embeddings"
index = pc.Index(index_name)

search_insurance_policies_tool = ChatCompletionToolParam(
    type="function",
    function={
        "name": "search_insurance_policies",
        "description": "Search for insurance policies based on a query",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for insurance policies",
                },
            },
            "required": ["query"],
        },
    },
)


def get_pinecone_docs(query: str, top_k: int = 5):
    query_embedding = (
        openai.embeddings.create(input=query, model="text-embedding-ada-002")
        .data[0]
        .embedding
    )

    # Query Pinecone to retrieve top-k relevant documents
    response = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    # Extract the text of the retrieved documents
    documents = [match["metadata"]["text"] for match in response["matches"]]
    return documents


async def search_insurance_policies(args):
    query = args.get("query")
    documents = get_pinecone_docs(query, top_k=3)
    return {
        "result": documents,
    }
