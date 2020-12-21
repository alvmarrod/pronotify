# -*- coding: utf-8 -*-
import os
import logging
import requests
import urllib.request
from bs4 import BeautifulSoup

if "pronotify" in __name__:
    import pronotify.library.database as database
else:
    import library.database as database

#######################################################################

def _check_coolmod_product(url) -> bool:
    """
    """

    result = False

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    availability = soup.find_all("span", 
                    {"class": "product-availability"}, limit=1)[0]
    
    for item in availability.strings:

        if "reserva" in item.lower():
            result = False
        elif "sin stock" in item.lower():
            result = False
        elif "envío inmediato" in item.lower():
            result = True

    return result

#######################################################################

class ProductLibrary:

    products = {}

    @staticmethod
    def add_product(url, group) -> bool:
        """
        
        Returns:
        - A `bool` indicating if the insertion was accomplished (true)
        """

        result = True

        if group == "":
            group = "default"
        
        if group in ProductLibrary.products:
            ProductLibrary.products[group][url] = False
        else:
            ProductLibrary.products[group] = {
                f"{url}": False
            }

        return result

    @staticmethod
    def del_product(url, group) -> bool:
        """
        
        Returns:
        - A `bool` indicating if the removal was accomplished (true)
        """

        result = True

        if group == "":
            group = "default"
        
        if group in ProductLibrary.products:
            if url in ProductLibrary.products[group]:
                del ProductLibrary.products[group][url]
            else:
                logging.warning(f"URL doesn't exist in this group!")
                result = False
        else:
            logging.warning(f"Group {group} doesn't exist!")
            result = False

        return result

    @staticmethod
    def check_products():
        """
        docstring
        """
        
        for group in ProductLibrary.products:

            for product in ProductLibrary.products[group]:

                if "coolmod" in product.lower():

                    ProductLibrary.products[group][product] = \
                        _check_coolmod_product(product)

                else:

                    logging.warning("Webpage not supported!")