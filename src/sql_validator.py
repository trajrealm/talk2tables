import sqlparse
import re
from sqlparse.sql import IdentifierList, Identifier, Function, Parenthesis, Token
from sqlparse.tokens import Keyword, DML, Whitespace, Punctuation, Name

def clean_sql(sql):
    # Remove ```sql ... ``` or ``` ... ``` wrappers
    sql = sql.strip()
    if sql.startswith("```"):
        sql = re.sub(r"```(?:sql)?\s*", "", sql)
        sql = sql.rstrip("`").strip()
    return sql
def extract_identifiers(sql):
    cleaned_sql = clean_sql(sql)
    parsed = sqlparse.parse(cleaned_sql)
    if not parsed:
        return set()
    stmt = parsed[0]
    identifiers = set()
    def extract_from_token(token, inside_function=False):
        if isinstance(token, IdentifierList):
            for sub in token.get_identifiers():
                extract_from_token(sub)
        elif isinstance(token, Identifier):
            if token.get_real_name() and not inside_function:
                identifiers.add(token.get_real_name())
            for sub in token.tokens:
                extract_from_token(sub)
        elif isinstance(token, Function):
            # Skip the function name (first token), parse only arguments
            for i, sub in enumerate(token.tokens):
                if i == 0 and sub.ttype == Name:
                    continue  # skip 'count'
                extract_from_token(sub, inside_function=True)
        elif isinstance(token, Parenthesis):
            for sub in token.tokens:
                extract_from_token(sub)
        elif token.ttype == Name and not inside_function:
            identifiers.add(token.value)

    for token in stmt.tokens:
        # print("token=", token, "\ttoken_type=", token.ttype, "\t token_type2=", type(token))
        extract_from_token(token)

    return identifiers
def validate_sql_against_schema(sql, schema_json):
    valid_tables = {table["name"] for table in schema_json["tables"]}
    valid_columns = set()
    for table in schema_json["tables"]:
        for col in table["columns"]:
            valid_columns.add(col["name"])
    identifiers = extract_identifiers(sql)
    print(identifiers)
    invalid_tables = identifiers - valid_tables - valid_columns

    return {
        "invalid_tables_or_columns": list(invalid_tables),
        "is_valid": len(invalid_tables) == 0
    }


if __name__ == "__main__":
    sql = " count(distinct security_id)"
    ids = extract_identifiers(sql)
    print(ids)