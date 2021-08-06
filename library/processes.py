# -*- coding: utf-8 -*-
import time
import logging
import requests
import platform

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

if "pronotify" in __name__:
    import pronotify.library.database as database
else:
    import library.database as database

#######################################################################

platforms = {
    "darwin": "./chromedriver/chromedriver",
    "windows": "./chromedriver/chromedriver.exe"
}
PLATFORM = platform.system().lower()
chromedriver_binary = platforms.get(PLATFORM, "./chromedriver/chromedriver")

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
        executable_path=chromedriver_binary,
        chrome_options=chrome_options)
    driver.get(url)
    if "pccomponentes" in url.lower():
        time.sleep(5)
    else:
        time.sleep(2)
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

    soup = _get_web_through_chromedriver(url, chromium_path)

    from IPython import embed
    embed()

    buy_button = soup.find_all("button",{"class": "js-article-buy"}, limit=1)
    if len(buy_button) > 0:
        buy_button = buy_button[0]
        available = "comprar" in buy_button.string.lower()
        logging.info(f"Availability: {buy_button.string.lower()}")

    full_price = soup.find_all("div", attrs={"class": "precioMain"}, limit=1)
    if len(full_price) > 0:
        full_price = full_price[0]
        price = float(full_price['data-price'])

    return (available, price)

def _check_neobyte_product(url, chromium_path) -> (bool, float):
    """
    Sample `chromium_path`:
    C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe
    """

    available = False
    price = float(0)

    soup = _get_web_through_chromedriver(url, chromium_path)

    dom_available = soup.find_all("span",{"id": "availability_value"}, limit=1)[0]
    available = "label-success" in dom_available.get('class')

    dom_price = soup.find_all("span",
                    {"id": "our_price_display"}, limit=1)[0].string
    price = float(dom_price.replace(" €", "").replace(",", "."))

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

            logging.info(f"Group {group}")

            for product in ProductLibrary.products[group]:

                logging.info(f"Checking {product}")

                if "coolmod" in product.lower():

                    ProductLibrary.products[group][product] = \
                        _check_coolmod_product(product, chromium_path)

                elif "pccomponentes" in product.lower():

                    ProductLibrary.products[group][product] = \
                        _check_pccomp_product(product, chromium_path)

                elif "neobyte" in product.lower():

                    ProductLibrary.products[group][product] = \
                        _check_neobyte_product(product, chromium_path)

                else:

                    logging.warning("Webpage not supported!")