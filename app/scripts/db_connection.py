import os
import sqlite3
import pandas as pd


def create_connection(db_file=None) -> sqlite3.Connection:
    file_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(file_dir)
    if db_file is None:
        db_file = os.path.join(base_dir, "data", "MyDB.db")
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    return sqlite3.connect(db_file)


def write_db(df: pd.DataFrame,
             table_name: str,
             exists: str = "replace",
             db_file: str = None):
    conn = create_connection(db_file)
    df.to_sql(table_name, conn, if_exists=exists, index=False)
    conn.close()


def read_db(table_name: str,
            db_file: str = None
            ) -> pd.DataFrame:
    conn = create_connection(db_file)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


def delete_db(table_name: str,
              db_file: str = None) -> None:
    conn = create_connection(db_file)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    conn.close()


def getdata(table_name: str, query: str, db_file: str = None) -> list:
    conn = create_connection(db_file)
    cursor = conn.cursor()
    sql_query = f"SELECT * FROM {table_name} WHERE {query}"

    try:
        cursor.execute(sql_query)
        data = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        data = []
    conn.close()
    if data == []:
        return []
    return data[0]


if __name__ == "__main__":
    # Example usage
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie']
    })
    try:
        write_db(df, 'test_table')
        print(read_db('test_table'))
        print(getdata('test_table', 'id = 1'))
        delete_db('test_table')
    except Exception as e:
        print(f"An error occurred: {e}")
