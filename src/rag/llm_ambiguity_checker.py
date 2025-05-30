# rag/llm_ambiguity_checker.py

from openai import OpenAI


def check_ambiguity(user_query: str, schema_text: str) -> dict:
    client = OpenAI()
    
    prompt = f"""
    You are an SQL assistant helping users query a database.

    Your task is to identify if a user's natural language query is ambiguous **based on the schema** provided.

    Only consider the question ambiguous if:
    - The user mentions a column name that appears in multiple tables, and the table is not specified
    - OR the table name is mentioned in a vague or partial way and could refer to multiple tables
    - OR the column is partially matched and could belong to multiple tables, with no table specified

    DO NOT consider the query ambiguous if:
    - The user has clearly specified the table and the column exists in that table, even if the column also exists elsewhere

    Output must be valid JSON.

    If ambiguity exists, return:
    {{
    "ambiguous": true,
    "clarify": [
        {{"term": "tm1", "matches": ["eatm1_score", "credit_tm1_score"]}},
        {{"term": "scores", "matches": ["tm1_scores", "growth_scores"]}}
    ]
    }}

    If there is no ambiguity, return:
    {{
    "ambiguous": false
    }}

    Schema:
    {schema_text}

    User Question:
    "{user_query}"

    Respond only with a valid JSON object.
    """


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    content = response.choices[0].message.content.strip()
    print("LLM Ambiguity Output:", content)

    try:
        return json.loads(content)
    except Exception as e:
        return {"ambiguous": False, "error": str(e)}
