# -*- coding: utf-8 -*-
import logging
import sqlite3

#######################################################################

def _create_products_table(con):
    """Creates the table for consolidated data.
    """

    tb_exists = "SELECT name FROM sqlite_master WHERE type='table' " + \
                "AND name='products'"

    if not con.execute(tb_exists).fetchone():

        logging.info("Table products not detected!")

        con.execute('''CREATE TABLE products
            (ID INTEGER PRIMARY KEY,
            URL            TEXT    NOT NULL,
            PRODUCT_GROUP  TEXT    NOT NULL,
            TIMESTAMP      DATETIME DEFAULT CURRENT_TIMESTAMP);''')

        logging.info("Table products created!")

#######################################################################

def _execute_non_reader_query(con, query) -> int:
    """Execute a non-reader query that returns a `int` value indicating
    if the execution was successful.

    If the command executed was an `update`, then the returned value
    indicates the number of rows that have been updated.
    """

    result = 1

    try:

        con.execute(query)

        commit_commands = [
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

def _execute_reader_query(con, query) -> tuple:
    """Execute a reader query that returns a `list` with the query
    response.
    """

    cursor = con.execute(query)
    rows = cursor.fetchall()

    return rows


#######################################################################

def open_database(db_file) -> sqlite3.Connection:
    """Open the specified file as a sqlite3 database file.

    Parameters:
    - A `str` with the filename of the database without extension

    Returns:
    - A `sqlite3.Connection` with the connection for the database
    """

    filepath = f"./data/{db_file}.db"
    con = None

    try:
        con = sqlite3.connect(filepath)
        _create_products_table(con)

    except Exception as e:

        logging.warning("Couldn't connect to the specified database" + \
                        f" \"{db_file}\"")
        logging.info(e)

    return con

def insert_product(con, data_tuple) -> bool:
    """Inserts the given data tuple into the products table.

    Parameters:
    - A `tuple` with 2 elements to be inserted into the table.

    Returns:
    - A `bool` indicating if the insertion was accomplished (true)
    """

    result = True

    if len(data_tuple) != 2:
        result = False
        logging.warning(f"product data was not length 2 but {len(data_tuple)}")
    else:
        query = "INSERT INTO products(" + \
                "URL, PRODUCT_GROUP) VALUES " + \
                "(\"" + '","'.join(str(i) for i in data_tuple) + "\")"
        result = (1 == _execute_non_reader_query(con, query))

    return result

def remove_product(con, data_tuple) -> bool:
    """Removes the given data tuple into the products table.

    Parameters:
    - A `tuple` with 2 elements to be removed from the table.

    Returns:
    - A `bool` indicating if the removal was accomplished (true)
    """

    result = True

    if len(data_tuple) != 2:
        result = False
        logging.warning(f"product data was not length 2 but {len(data_tuple)}")
    else:
        query = "DELETE FROM products WHERE " + \
                f"URL = \"{data_tuple[0]}\" " + \
                f"AND PRODUCT_GROUP = \"{data_tuple[1]}\""
        result = (1 == _execute_non_reader_query(con, query))

    return result

def read_products_by_group(con, group) -> tuple:
    """Queries the products table by group.
    """

    query = "SELECT ID, URL, PRODUCT_GROUP " + \
            " FROM products" + \
            f" WHERE PRODUCT_GROUP=\"{group}\""

    result = None

    try:
        result = _execute_reader_query(con, query)

    except Exception as e:
        logging.warning(f"Couldn't retrieve data for the given group: {group}")
        logging.info(e)

    return result

def read_products_by_vendor(con, vendor) -> tuple:
    """Queries the products table by vendor, that should be present in the URL.
    """

    query = "SELECT ID, URL, PRODUCT_GROUP " + \
            " FROM products" + \
            f" WHERE LOCATE({vendor.lower()}, URL) > 0"

    result = None

    try:
        result = _execute_reader_query(con, query)

    except Exception as e:
        logging.warning(f"Couldn't get data for the given vendor: {vendor}")
        logging.info(e)

    return result

def read_products(con) -> tuple:
    """Queries the products table and retrieves the products,
    ordered by insertion time.
    """

    query = "SELECT ID, URL, PRODUCT_GROUP " + \
            " FROM products"

    result = None

    try:
        result = _execute_reader_query(con, query)

    except Exception as e:
        logging.warning(f"Couldn't retrieve data for products table")
        logging.info(e)

    return result

def close_database(con):
    """Close the given database connection

    Parameters:
    - A `sqlite3.Connection` to be closed
    """

    try:
        con.close()

    except Exception as e:

        logging.warning("Couldn't close the specified database" + \
                        " \"{db_file}\"")
        logging.info(e)