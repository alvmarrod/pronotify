import os
import time
import emoji
import sqlite3
import logging
import platform
from typing import Optional, Callable, TypedDict

from urllib.parse import urlparse, uses_relative
from datetime import datetime as dt

from library.emojis import *
import library.database as db
import library.processes as processes

if "pronotify" in __name__:
    import pronotify.main as main # type: ignore
else:
    import main as main

DB_NAME: str = "pronotify"
POLL_SECONDS: int = 30

platforms: dict[str, str] = {
    "darwin": "clear",
    "windows": "cls"
}

PLATFORM: str = platform.system().lower()
CLEAN_CMD: str = platforms.get(PLATFORM, "clear")

CHROMIUM_PATH: Optional[str] = None

class MenuOption(TypedDict):
    text: str
    function: Callable[[sqlite3.Connection], None]

def _ask_bool_user(msg: str, default:bool = False) -> bool:
    """Ask anything to the user and returns a boolean.

    If the pattern is not followed, returns false.
    """
    result: bool = default

    try:
        
        option: str = input(f"{msg} (Y/N): ")
        if option.lower() == "y":
            result = True
        elif option.lower() == "n":
            result = False
            
    except ValueError as e:
        print(f"Error! {e}")

    return result

def _ask_str_user(msg: str, default: str = "") -> str:
    """Ask anything to the user and returns the answer
    """

    result: str = input(f"{msg}: ")
    if len(result) == 0:
        result = default

    return result

def _ask_int_user(msg: str, default: int = 0) -> int:
    """Ask anything to the user and returns an int.
    """
    result: int = default

    try:
        option: str  = input(f"{msg}: ")
        result = int(option)
            
    except ValueError as e:
        print(f"Error! {e}")

    return result

def _ask_back_to_menu() -> bool:
    """Checks if the user wants to go back to the menu
    """
    result: bool = False

    try:
        option: str = input("Do you want to go back to menu? (Y/N): ")

        if option.lower() == "y":
            result = True

    except ValueError as e:
        print(f"Error! {e}")

    return result

def _exit_program(db_conn: sqlite3.Connection) -> None:
    """Exit the program gracefully."""
    print("Goodbye!")

def generate_menu(db_conn: sqlite3.Connection) -> bool:
    """Generates the menu options. If returns false means the
    menu should be finished.

    Receives the database connection as parameter.
    """
    show_again: bool = False

    options: dict[int, MenuOption] = {
        1: {
            "text": "Add product",
            "function": add_product
        },
        2: {
            "text": "Remove product",
            "function": del_product
        },
        3: {
            "text": "Show status",
            "function": check_products
        },
        4: {
            "text": "Exit",
            "function": _exit_program
        }
    }

    if not main.DEBUG:
        os.system(CLEAN_CMD)

    print("############### pronotify ###############")
    print("####                               ####")

    lon = len("############### pronotify ###############")
    for i in range(1, len(options)+1):
        opt = f'# {i}. {options[i]["text"]}'
        if len(opt) < lon:
            opt += " " * (lon-(len(opt)+1)) + "#"
        print(opt)

    print("####                               ####")
    print("#######################################")

    print("")

    try:

        option: int = int(input("Choose an option: "))

        if option <= 0 or option > len(options):
            raise ValueError("Option number not recognised")

        show_again = True

        if options[option]["function"]:
            options[option]["function"](db_conn)
        else:
            raise ValueError(f"Option {option} is not available!")

    except ValueError as e:
        logging.error(f"{e}\n")

    if not _ask_back_to_menu():
        show_again = False

    return show_again

#######################################################################

def load_product(product: tuple) -> None:
    """Loads a product from the DB into memory.
    """
    #product_id: int = product[0]
    product_url: str = product[1]
    product_group: str = product[2]

    if not processes.ProductLibrary.add_product(product_url, product_group):
        logging.warning(f"Failed to load product {product} into memory...")

#######################################################################

def add_product(db_conn: sqlite3.Connection) -> None:
    """Adds a product to the memory and to the DB.
    """

    product_url: str = _ask_str_user("Please, insert URL to the product")
    logging.debug(f"Product URL: {product_url}")

    product_group: str = _ask_str_user("Specify a group if desired", "")
    logging.debug(f"Product Group: {product_group}")

    if not processes.ProductLibrary.add_product(product_url, product_group):
        logging.warning(f"Product not saved in memory!")
    elif not db.insert_product(db_conn, (product_url, product_group)):
        logging.warning(f"Product not saved in DB!")
    else:
        print(f"Product added successfully :)")

#######################################################################

def del_product(db_conn: sqlite3.Connection):
    """Deletes a product from memory and from the DB.
    """

    product_url: str = _ask_str_user("Please, insert URL to remove")
    logging.debug(f"Product URL: {product_url}")

    product_group: str = _ask_str_user("Specify a group where it belongs", "")
    logging.debug(f"Product Group: {product_group}")

    if not processes.ProductLibrary.del_product(product_url, product_group):
        logging.warning(f"Product not found in memory!")
    elif not db.remove_product(db_conn, (product_url, product_group)):
        logging.warning(f"Product was not found in DB!")
    else:
        print(f"Product removed successfully :)")

#######################################################################

def check_products(db_conn: sqlite3.Connection) -> None:
    """
    Checks the products in memory and shows their status.

    db_conn parameters is not used, but is defined to avoid more complex
    parameters management in main function menu.
    """
    check: bool = True

    while check:
        try:
            # Update data
            assert CHROMIUM_PATH is not None, "Chromium path is not set!"
            processes.ProductLibrary.check_products(CHROMIUM_PATH)

            if not main.DEBUG:
                os.system(CLEAN_CMD)
            print(emoji.emojize(f"{ETIME} Last Update {dt.now()} {ETIME}")
            )
            print("")

            for group in processes.ProductLibrary.products:

                print(emoji.emojize(f"{EGROUP} {group} {EGROUP}")
                )
                print("")

                for product in processes.ProductLibrary.products[group]:

                    # vendor = urlparse(product).netloc

                    try:
                        availability, price = \
                            processes.ProductLibrary.products[group][product]
                    except Exception as e:
                        logging.warning(f"Error: {e}")
                        availability = False
                        price = -1

                    print(f"Product URL: {product}")

                    if availability:
                        availability = EVALID
                    else:
                        availability = ECROSS
                    print(emoji.emojize(f"Availability: {availability} - Price: {price}€"))

                print("")

            print(f"++ Control ++")
            print(f"Please, hit Ctrl+C in case you want to stop monitoring...")

            time.sleep(POLL_SECONDS)

        except KeyboardInterrupt:
            check = False

#######################################################################

def menu() -> None:
    """Generates and controls the menu for the app.
    """

    db_conn = db.open_database(DB_NAME)
    if not db_conn:
        logging.error("Database connection could not be established!")
        return

    # Database setup
    print(f"1. Checking and creating products table in DB...")
    db._create_products_table(db_conn)

    print(f"2. Loading database into memory...")
    products = db.read_products(db_conn)

    if products:
        for item in products:
            load_product(item)

    # Menu
    generate = generate_menu(db_conn)

    while generate:
        generate = generate_menu(db_conn)

    db.close_database(db_conn)
