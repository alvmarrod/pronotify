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
    
    if availability.div:
        availability = availability.div.contents[0].string
    else:
        availability = availability.string

    if "reserva" not in availability.lower():
        pass
    elif "sin stock" not in availability.lower():
        pass
    elif "envío inmediato" in availability.lower():
        result = True

    return result

#######################################################################

class ProductLibrary:

    products = {}

    @staticmethod
    def add_product(url, group):
        """
        docstring
        """

        if group == "":
            group = "default"
        
        if group in ProductLibrary.products:
            ProductLibrary.products[group][url] = False
        else:
            ProductLibrary.products[group] = {
                f"{url}": False
            }

    @staticmethod
    def del_product(url, group):
        """
        docstring
        """

        if group == "":
            group = "default"
        
        if group in ProductLibrary.products:
            if url in ProductLibrary.products[group]:
                del ProductLibrary.products[group][url]
            else:
                logging.warning(f"URL doesn't exist in this group!")    
        else:
            logging.warning(f"Group {group} doesn't exist!")

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
