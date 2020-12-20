# -*- coding: utf-8 -*-
import logging
import sqlite3

#######################################################################

def _create_all_movements_table(con):
    """Creates the table for consolidated data. This function is
    idempotent, so it will not overwrite an existing config file.
    """

    tb_exists = "SELECT name FROM sqlite_master WHERE type='table' " + \
                "AND name='all_movements'"

    if not con.execute(tb_exists).fetchone():

        logging.info("Table all_movements not detected!")

        con.execute('''CREATE TABLE all_movements
            (ID INTEGER PRIMARY KEY,
            OP_DATE        TEXT    NOT NULL,
            VAL_DATE       TEXT    NOT NULL,
            CONCEPT        TEXT    NULL,
            AMOUNT         REAL,
            BALANCE        REAL,
            TIMESTAMP      DATETIME DEFAULT CURRENT_TIMESTAMP);''')

        logging.info("Table all_movements created!")

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
        _create_all_movements_table(con)

    except Exception as e:

        logging.warning("Couldn't connect to the specified database" + \
                        f" \"{db_file}\"")
        logging.info(e)

    return con

def insert_movement(con, data_tuple) -> bool:
    """Inserts the given data tuple into the all_movements table.

    Parameters:
    - A `tuple` with 5 elements to be inserted into the table.

    Returns:
    - A `bool` indicating if the insertion was accomplished (true)
    """

    result = True

    if len(data_tuple) != 5:
        result = False
        logging.warning(f"Movement data was not length 5 but {len(data_tuple)}")
    else:
        query = "INSERT INTO all_movements(" + \
                "OP_DATE, VAL_DATE, CONCEPT, AMOUNT, BALANCE) VALUES " + \
                "(\"" + '","'.join(str(i) for i in data_tuple) + "\")"
        result = (1 == _execute_non_reader_query(con, query))

    return result

def read_movements_by_op_date(con, date) -> tuple:
    """Queries the all_movements table by operation date and retrieves the 
    movements, ordered by insertion time.
    """

    query = "SELECT ID, OP_DATE, VAL_DATE, CONCEPT, AMOUNT, BALANCE" + \
            " FROM all_movements" + \
            f" WHERE OP_DATE=\"{date}\""

    result = None

    try:
        result = _execute_reader_query(con, query)

    except Exception as e:
        logging.warning(f"Couldn't retrieve data for the given date: {date}")
        logging.info(e)

    return result

def read_movements_by_val_date(con, date) -> tuple:
    """Queries the all_movements table by value date and retrieves the
    movements, ordered by insertion time.
    """

    query = "SELECT ID, OP_DATE, VAL_DATE, CONCEPT, AMOUNT, BALANCE" + \
            " FROM all_movements" + \
            f" WHERE VAL_DATE=\"{date}\""

    result = None

    try:
        result = _execute_reader_query(con, query)

    except Exception as e:
        logging.warning(f"Couldn't retrieve data for the given date: {date}")
        logging.info(e)

    return result

def read_movements_by_amount(con, amount) -> tuple:
    """Queries the all_movements table by transaction amount and returns
    all the movements that match this amount.
    """

    query = "SELECT ID, OP_DATE, VAL_DATE, CONCEPT, AMOUNT, BALANCE" + \
            " FROM all_movements" + \
            f" WHERE AMOUNT={amount}"

    result = None

    try:
        result = _execute_reader_query(con, query)

    except Exception as e:
        logging.warning(f"Couldn't get data for the given amount: {amount}")
        logging.info(e)

    return result

def read_movements_by_amount_range(con, min, max) -> tuple:
    """Queries the all_movements table by transaction amount and returns
    all the movements that match this amount.

    The function is capable of switching boundaries if mistaken.

    Parameters:
    - A `sqlite3.Connection` to the database
    - A `double` with the lower threshold. None means no boundary.
    - A `double` with the upper threshold. None means no boundary.

    Returns:
    - A `tuple` with the results
    """

    if min and max:
        if min > max:
            toggle = min
            min = max
            max = toggle

    if min:
        aux =  f" WHERE AMOUNT >= {min}"

    if max:
        if len(aux) > 0:
            aux += f" AND AMOUNT <= {max}"
        else:
            aux = f" WHERE AMOUNT <= {max}"

    query = "SELECT ID, OP_DATE, VAL_DATE, CONCEPT, AMOUNT, BALANCE" + \
            f" FROM all_movements {aux}"

    result = None

    try:
        result = _execute_reader_query(con, query)

    except Exception as e:
        logging.warning(f"Couldn't get data for the given range: {min}, {max}")
        logging.info(e)

    return result

def read_movements_by_balance_range(con, min, max) -> tuple:
    """Queries the all_movements table by balance amount and returns
    all the movements that match this range.

    The function is capable of switching boundaries if mistaken.

    Parameters:
    - A `sqlite3.Connection` to the database
    - A `double` with the lower threshold. None means no boundary.
    - A `double` with the upper threshold. None means no boundary.

    Returns:
    - A `tuple` with the results
    """

    if min and max:
        if min > max:
            toggle = min
            min = max
            max = toggle

    if min:
        aux =  f" WHERE BALANCE >= {min}"

    if max:
        if len(aux) > 0:
            aux += f" AND BALANCE <= {max}"
        else:
            aux = f" WHERE BALANCE <= {max}"

    query = "SELECT ID, OP_DATE, VAL_DATE, CONCEPT, AMOUNT, BALANCE" + \
            f" FROM all_movements {aux}"

    result = None

    try:
        result = _execute_reader_query(con, query)

    except Exception as e:
        logging.warning(f"Couldn't get data for the given range: {min}, {max}")
        logging.info(e)

    return result

def read_movements(con) -> tuple:
    """Queries the all_movements table and retrieves the movements,
    ordered by insertion time.
    """

    query = "SELECT ID, OP_DATE, VAL_DATE, CONCEPT, AMOUNT, BALANCE" + \
            " FROM all_movements"

    result = None

    try:
        result = _execute_reader_query(con, query)

    except Exception as e:
        logging.warning(f"Couldn't retrieve data for all_movements table")
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