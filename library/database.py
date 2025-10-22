import logging
import sqlite3

from typing import Optional

#######################################################################

def _create_products_table(con: sqlite3.Connection):
    """Creates the table for consolidated data.
    If the table already exists, then nothing is done.
    """

    tb_exists: str = (
        "SELECT name FROM sqlite_master "
        "WHERE type='table' "
        "AND name='products'"
    )

    if not con.execute(tb_exists).fetchone():

        logging.info("Table 'products' not detected!")

        con.execute('''CREATE TABLE products
            (ID INTEGER PRIMARY KEY,
            URL            TEXT    NOT NULL,
            PRODUCT_GROUP  TEXT    NOT NULL,
            TIMESTAMP      DATETIME DEFAULT CURRENT_TIMESTAMP);''')

        logging.info("Table 'products' created!")

#######################################################################

def _execute_non_reader_query(con: sqlite3.Connection, query: str) -> int:
    """Execute a non-reader query that returns an `int` value indicating
    if the execution was successful.

    If the command executed was an `update`, then the returned value
    indicates the number of rows that have been updated.
    """
    result: int = 1

    try:

        con.execute(query)

        commit_commands: list[str] = [
            "insert",
            "update",
            "delete"
        ]

        if query.split(" ")[0].lower() in commit_commands:
            con.commit()

        if query.split(" ")[0].lower() == "update":
            result = con.total_changes

    except Exception as e:
        result = 0
        logging.warning(f"Couldn't execute non-reader query: \"{query}\"")
        logging.info(e)

    return result

def _execute_reader_query(con: sqlite3.Connection, query: str) -> list:
    """Execute a reader query that returns a `list` with the query
    response.
    """
    cursor: sqlite3.Cursor = con.execute(query)
    rows: list = cursor.fetchall()

    return rows


#######################################################################

def open_database(db_file: str) -> Optional[sqlite3.Connection]:
    """Open the specified file as a sqlite3 database file.

    Parameters:
    - A `str` with the filename of the database without extension

    Returns:
    - A `sqlite3.Connection` with the connection for the database
    """
    filepath: str = f"./data/{db_file}.db"
    con: Optional[sqlite3.Connection] = None

    try:
        con = sqlite3.connect(filepath)
        _create_products_table(con)

    except Exception as e:
        logging.warning("Couldn't connect to the specified database" + \
                        f" \"{db_file}\"")
        logging.info(e)

    return con

def insert_product(con: sqlite3.Connection, data_tuple: tuple) -> bool:
    """Inserts the given data tuple into the products table.

    Parameters:
    - A `tuple` with 2 elements to be inserted into the table.

    Returns:
    - A `bool` indicating if the insertion was accomplished (true)
    """
    result: bool = True

    if len(data_tuple) != 2:
        result = False
        logging.warning(f"product data was not length 2 but {len(data_tuple)}")
    else:
        query = "INSERT INTO products(" + \
                "URL, PRODUCT_GROUP) VALUES " + \
                "(\"" + '","'.join(str(i) for i in data_tuple) + "\")"
        result = (1 == _execute_non_reader_query(con, query))

    return result

def remove_product(con: sqlite3.Connection, data_tuple: tuple) -> bool:
    """Removes the given data tuple into the products table.

    Parameters:
    - A `tuple` with 2 elements to be removed from the table.

    Returns:
    - A `bool` indicating if the removal was accomplished (true)
    """
    result: bool = True

    if len(data_tuple) != 2:
        result = False
        logging.warning(f"product data was not length 2 but {len(data_tuple)}")
    else:
        query = "DELETE FROM products WHERE " + \
                f"URL = \"{data_tuple[0]}\" " + \
                f"AND PRODUCT_GROUP = \"{data_tuple[1]}\""
        result = (1 == _execute_non_reader_query(con, query))

    return result

def read_products_by_group(con: sqlite3.Connection, group: str) -> Optional[list]:
    """Queries the products table by group.
    """
    result: Optional[list] = None

    query:str = (
        "SELECT ID, URL, PRODUCT_GROUP "
        " FROM products"
        f" WHERE PRODUCT_GROUP=\"{group}\""
    )

    try:
        result = _execute_reader_query(con, query)

    except Exception as e:
        logging.warning(f"Couldn't retrieve data for the given group: {group}")
        logging.info(e)

    return result

def read_products_by_vendor(con: sqlite3.Connection, vendor: str) -> Optional[list]:
    """Queries the products table by vendor, that should be present in the URL.
    """
    result: Optional[list] = None

    query = (
        "SELECT ID, URL, PRODUCT_GROUP "
        " FROM products"
        f" WHERE LOCATE({vendor.lower()}, URL) > 0"
    )

    try:
        result = _execute_reader_query(con, query)

    except Exception as e:
        logging.warning(f"Couldn't get data for the given vendor: {vendor}")
        logging.info(e)

    return result

def read_products(con: sqlite3.Connection) -> Optional[list]:
    """Queries the products table and retrieves the products,
    ordered by insertion time.
    """
    result: Optional[list] = None

    query = (
        "SELECT ID, URL, PRODUCT_GROUP " + \
        " FROM products"
    )

    try:
        result = _execute_reader_query(con, query)

    except Exception as e:
        logging.warning(f"Couldn't retrieve data for products table")
        logging.info(e)

    return result

def close_database(con: sqlite3.Connection):
    """Close the given database connection
    """
    try:
        con.close()

    except Exception as e:
        logging.warning("Couldn't close the specified database" + \
                        " \"{db_file}\"")
        logging.info(e)
