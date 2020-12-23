# -*- coding: utf-8 -*-
import os
import time
import logging
import requests
import urllib.request

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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

def _check_pccomp_product(url) -> bool:
    """
    """

    result = False

    logging.info(f"PCComp article: {url}")

    # Prepare options for the chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("--window-size=1920x1080")

    # Just in case of windows execution
    # https://bugs.chromium.org/p/chromium/issues/detail?id=737678
    chrome_options.add_argument('--disable-gpu')

    # Supress chrome logs
    # https://stackoverflow.com/questions/47392423/python-selenium-devtools-listening-on-ws-127-0-0-1
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # start chrome browser
    driver = webdriver.Chrome(
        executable_path="./chromedriver/chromedriver.exe",
        chrome_options=chrome_options)
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source.encode("utf-8"), "html.parser")
    driver.quit()

    artcl_is = soup.find_all("div",{"id": "articleInStock"}, limit=1)[0]
    artcl_is_style = artcl_is.get('style')
    logging.info(f"PCComp, article IS style: {artcl_is_style}")

    artcl_oos = soup.find_all("div",{"id": "articleOutOfStock"}, limit=1)[0]
    artcl_oos_style = artcl_oos.get('style')
    logging.info(f"PCComp, article OOS style: {artcl_oos_style}")
    logging.info(f"PCComp, article OOS Complete: {artcl_oos}")
    
    if "display:none;" in artcl_oos_style:
        result = True

    if "" == artcl_is_style:
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

                elif "pccomponentes" in product.lower():

                    ProductLibrary.products[group][product] = \
                        _check_pccomp_product(product)

                else:

                    logging.warning("Webpage not supported!")