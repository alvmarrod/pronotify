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

def _get_web_through_chromedriver(url, chromium_path) -> BeautifulSoup:
    """
    """

    # Prepare options for the chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("--window-size=1920x1080")

    # Just in case of windows execution
    # https://bugs.chromium.org/p/chromium/issues/detail?id=737678
    chrome_options.add_argument('--disable-gpu')

    if chromium_path:
        chrome_options.binary_location = chromium_path

    # Supress chrome logs
    # https://stackoverflow.com/questions/47392423/python-selenium-devtools-listening-on-ws-127-0-0-1
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # start chrome browser
    driver = webdriver.Chrome(
        executable_path="./chromedriver/chromedriver.exe",
        chrome_options=chrome_options)
    driver.get(url)
    if "pccomponentes" in url.lower():
        time.sleep(10)
    else:
        time.sleep(1)
    soup = BeautifulSoup(driver.page_source.encode("utf-8"), "html.parser")
    driver.quit()

    return soup

def _check_coolmod_product(url, chromium_path) -> (bool, float):
    """
    """

    available = False
    price = float(0)

    # soup = _get_web_through_chromedriver(url, chromium_path)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    availability = soup.find_all("span", 
                    {"class": "product-availability"}, limit=1)[0]
    
    for item in availability.strings:

        if "reserva" in item.lower():
            available = False
        elif "sin stock" in item.lower():
            available = False
        elif "envío inmediato" in item.lower():
            available = True

    main_price = soup.find_all("span",
                    {"class": "text-price-total"}, limit=1)[0].string
    sup_price = soup.find_all("span",
                    {"class": "text-price-total-sup"}, 
                    limit=1)[0].string.replace(",", "").replace("€", "")

    price = float(main_price) + float(sup_price)/100

    return (available, price)

def _check_pccomp_product(url, chromium_path) -> (bool, float):
    """
    Sample `chromium_path`:
    C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe
    """

    available = False
    price = float(0)

    logging.info(f"PCComp article: {url}")
    soup = _get_web_through_chromedriver(url, chromium_path)

    artcl_is = soup.find_all("div",{"id": "articleInStock"}, limit=1)[0]
    artcl_is_style = artcl_is.get('style')
    logging.info(f"PCComp, article IS style: {artcl_is_style}")

    artcl_oos = soup.find_all("div",{"id": "articleOutOfStock"}, limit=1)[0]
    artcl_oos_style = artcl_oos.get('style')
    logging.info(f"PCComp, article OOS style: {artcl_oos_style}")
    logging.info(f"PCComp, article OOS Complete: {artcl_oos}")
    
    if "display:none;" in artcl_oos_style:
        available = True

    if "" == artcl_is_style:
        available = True

    main_price = soup.find_all("span",
                    {"class": "baseprice"}, limit=1)[0].string
    sup_price = soup.find_all("span",
                    {"class": "cents"})[0].string

    if sup_price:
        sup_price = sup_price.replace(",", "")
    else:
        sup_price = 0

    price = float(main_price) + float(sup_price)/100

    return (available, price)

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
    def check_products(chromium_path):
        """
        docstring
        """
        
        for group in ProductLibrary.products:

            for product in ProductLibrary.products[group]:

                if "coolmod" in product.lower():

                    ProductLibrary.products[group][product] = \
                        _check_coolmod_product(product, chromium_path)

                elif "pccomponentes" in product.lower():

                    ProductLibrary.products[group][product] = \
                        _check_pccomp_product(product, chromium_path)

                else:

                    logging.warning("Webpage not supported!")