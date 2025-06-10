from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


def get_qa_chain(vectorstore, model_name="gpt-4o-mini"):
    prompt_template = """
    You are a SQL assistant that generates SQL and identifiers if the user wants to visaulize the results based on the user's question and the schema below.

    You can also answer metadata questions about the schema itself using standard SQL patterns, such as:
    - Listing tables: SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
    - Counting tables: SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';
    - Listing columns: SELECT column_name FROM information_schema.columns WHERE table_name = 'your_table';
    
    You will return a JSON object with:
    - "sql": SQL query to run
    - "plot": true or false, if the user wants to visualize the results
    - "x_axis": (if plot) column name for x-axis
    - "y_axis": (if plot) column name for y-axis
    - "chart_type": (if plot) "bar" or "line" or "pie"

    Output ONLY the SQL — no commentary, no additional explanation.
    -DO NOT include ```JSON or ``` at the beginning or end of the response.

    ---

    SCHEMA:
    {context}

    QUESTION:
    {question}

    RESPONSE:
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


