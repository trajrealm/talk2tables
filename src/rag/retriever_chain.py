from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

def get_qa_chain(vectorstore, model_name="gpt-4o-mini"):
    prompt_template = """You are an expert SQL assistant. Given a user's question and the database schema below, generate a valid SQL query.

⚠️ IMPORTANT:
- ONLY use tables and columns shown in the schema.
- NEVER make up table or column names.
- If the required table or column is not in the schema, say "I can't find a match in the schema."

---

SCHEMA:
{context}

---

QUESTION:
{question}

---

SQL:"""

    prompt = PromptTemplate.from_template(prompt_template)

    retriever = vectorstore.as_retriever()
    llm = ChatOpenAI(model_name=model_name, temperature=0)

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )

    return chain
