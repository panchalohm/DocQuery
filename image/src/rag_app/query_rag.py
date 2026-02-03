from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .get_chroma_db import get_chroma_db

load_dotenv()

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

OPENAI_MODEL = "gpt-4o-mini"


@dataclass
class QueryResponse:
    query_text: str
    response_text: str
    sources: List[str]


def query_rag(query_text: str) -> QueryResponse:
    db = get_chroma_db()

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=3)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    model = ChatOpenAI(model=OPENAI_MODEL, temperature=0)
    response = model.invoke(prompt)
    response_text = response.content

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    print(f"Response: {response_text}\nSources: {sources}")

    return QueryResponse(
        query_text=query_text, response_text=response_text, sources=sources
    )


if __name__ == "__main__":
    query_rag("How much does a landing page cost to develop?")