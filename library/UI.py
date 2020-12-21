# -*- coding: utf-8 -*-
import os
import time
import emoji
import logging
import platform

from urllib.parse import urlparse
from datetime import datetime as dt
import library.processes as processes

if "pronotify" in __name__:
    import pronotify.main as main
else:
    import main as main

PLATFORM = platform.system().lower()
CLEAN_CMD = "cls" if "win" in PLATFORM else "clear"

def _ask_bool_user(msg, default=False) -> bool:
    """Ask anything to the user and returns a boolean.

    If the pattern is not followed, returns false.
    """

    result = default
    try:
        
        option = input(f"{msg} (Y/N): ")
        if option.lower() == "y":
            result = True
        elif option.lower() == "n":
            result = False
            
    except ValueError as e:
        print(f"Error! {e}")

    return result

def _ask_str_user(msg, default="") -> str:
    """Ask anything to the user and returns the answer
    """

    result = input(f"{msg}: ")
    if len(result) == 0:
        result = default

    return result

def _ask_int_user(msg, default=0) -> int:
    """Ask anything to the user and returns an int.
    """

    result = default
    try:
        
        option = input(f"{msg}: ")
        result = int(option)
            
    except ValueError as e:
        print(f"Error! {e}")

    return result

def _ask_loop(asktype, msg, default_value, failcheck, checkparameters=None):
    """Handles asking to the user several times until the desired value
    to be used is agreed.

    A fail check function can be provided to run over the given result,
    which will be passed as parameter to it. A tuple with parameters can
    be provided to feed that function, where the result from the input
    will be appended.
    
    If the failcheck returns `true`, it will trigger a rollback to the
    `default_value` given.
    """

    result = None
    again = True
    function = None

    if "str" == asktype.lower():
        function = _ask_str_user
    elif "bool" == asktype.lower():
        function = _ask_bool_user
    elif "int" == asktype.lower():
        function = _ask_int_user

    if function:

        while again == True:

            result = function(msg, default=default_value)

            parameters = (*checkparameters, result)
            #from IPython import embed
            #embed()
            if failcheck(*parameters):

                result = default_value
                print(f"Error! {parameters[-1]} value is not correct." + \
                        " Rolling back...")

            else:
                
                if result != default_value:
                    ask_again = f"Input given is \"{result}\", do you agree?"
                    again = _ask_bool_user(ask_again)
                else:
                    again = False

    return result

def _ask_back_to_menu() -> bool:
    """Checks if the user wants to go back to the menu
    """

    result = False

    try:
        
        option = input("Do you want to go back to menu? (Y/N): ")
        
        if option.lower() == "y":
            result = True
            
    except ValueError as e:
        print(f"Error! {e}")

    return result

def _menu_generation() -> bool:
    """Generates the menu options. If returns false means the
    menu should be finished
    """

    show_again = False

    options = {
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
            "function": exit
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

        option = int(input("Choose an option: "))

        if option <= 0 or option > len(options):
            raise ValueError("Option number not recognised")

        show_again = True

        if options[option]["function"]:
            options[option]["function"]()
        else:
            raise ValueError(f"Option {option} is not available!")

    except ValueError as e:

        print(f"Error! {e}\n")

    if not _ask_back_to_menu():
        show_again = False
    
    return show_again

#######################################################################

def add_product():
    """
    """

    product_url = _ask_str_user("Please, insert URL to the product")
    logging.debug(f"Product URL: {product_url}")

    product_group = _ask_str_user("Specify a group if desired", "")
    logging.debug(f"Product Group: {product_group}")

    processes.ProductLibrary.add_product(product_url, product_group)

#######################################################################

def del_product():
    """
    """

    product_url = _ask_str_user("Please, insert URL to remove")
    logging.debug(f"Product URL: {product_url}")

    product_group = _ask_str_user("Specify a group where it belongs", "")
    logging.debug(f"Product Group: {product_group}")

    processes.ProductLibrary.del_product(product_url, product_group)

#######################################################################

def check_products():
    """
    """

    check = True

    while check:

        try:

            # Update data
            processes.ProductLibrary.check_products()

            # Print it
            os.system(CLEAN_CMD)
            print(f"+++++ Update Time +++++")
            print(f"{dt.now()}")
            print("")
            
            for group in processes.ProductLibrary.products:

                print(f"+++ {group} +++")
                print("")

                for product in processes.ProductLibrary.products[group]:

                    vendor = urlparse(product).netloc
                    availability = processes.ProductLibrary.products[group][product]
                    print(f"Vendor: {vendor}")
                    print(f"URL: {product}")
                    
                    print(f"Availability source: {availability}")
                    if availability:
                        availability = ":white_check_mark:"
                    else:
                        availability = ":x:"
                    print(emoji.emojize(f"Availability: {availability}",
                            use_aliases=True))

                print("")

                print(f"++ Control ++")
                print(f"Please, hit Ctrl+C in case you want to stop monitoring...")
            
            time.sleep(10)
        
        except KeyboardInterrupt:
            check = False

#######################################################################

def menu():
    """Generates and controls the menu for the app.
    """

    generate = _menu_generation()

    while generate:
        generate = _menu_generation()
