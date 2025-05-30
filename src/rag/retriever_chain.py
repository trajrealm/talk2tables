from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


def get_qa_chain(vectorstore, model_name="gpt-4o-mini"):
    prompt_template = """
    You are a SQL assistant that generates SQL based on the user's question and the schema below.

    You can also answer metadata questions about the schema itself using standard SQL patterns, such as:
    - Listing tables: SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
    - Counting tables: SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';
    - Listing columns: SELECT column_name FROM information_schema.columns WHERE table_name = 'your_table';
    
    Output ONLY the SQL — no commentary, no additional explanation.

    ---

    SCHEMA:
    {context}

    QUESTION:
    {question}

    SQL:
    """

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
