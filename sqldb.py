import pandas as pd
from sqlalchemy import create_engine
import urllib

connection_string = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=AdventureWorks2025;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={connection_string}"
)


def execute_query(query):
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df

query = '''
SELECT TOP 10
    BusinessEntityID,
    FirstName,
    LastName
FROM Person.Person
'''

def get_table_schema(table_name):
    if "." in table_name:
        schema_name, table_only = table_name.split(".", 1)
    else:
        schema_name = "dbo"
        table_only = table_name

    query = f"""
        SELECT
            s.name AS SchemaName,
            t.name AS TableName,
            c.name AS ColumnName,
            ty.name AS DataType            
        FROM sys.tables t
        INNER JOIN sys.schemas s
            ON t.schema_id = s.schema_id
        INNER JOIN sys.columns c
            ON t.object_id = c.object_id
        INNER JOIN sys.types ty
            ON c.user_type_id = ty.user_type_id
        WHERE s.name = '{schema_name}'
          AND t.name = '{table_only}'
        ORDER BY c.column_id
    """

    schema = execute_query(query)

    return schema


# result = get_table_schema("Person.Person")

# print(result)