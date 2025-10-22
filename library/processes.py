import time
import logging
import requests
import platform

from typing import TypedDict
from types import FunctionType

from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

if "pronotify" in __name__:
    import pronotify.library.database as database # type: ignore
else:
    import library.database as database

#######################################################################

platforms: dict[str, str] = {
    "darwin": "./chromedriver/chromedriver",
    "windows": "./chromedriver/chromedriver.exe"
}

PLATFORM: str = platform.system().lower()
chromedriver_binary: str = platforms.get(PLATFORM, "./chromedriver/chromedriver")

#######################################################################

def _get_web_through_chromedriver(url: str,
                                  chromium_path: str,
                                  slowcon: int = 1) -> BeautifulSoup:
    """Get the webpage through a chromium driver. For slow connections,
    increase the `slowcon` parameter (1 is default, 2 is double load time, etc).
    """
    # Prepare options for the chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-infobars')

    # Just in case of windows execution
    # https://bugs.chromium.org/p/chromium/issues/detail?id=737678
    if platform.system().lower() == "windows":
        chrome_options.add_argument('--disable-gpu')

    if len(chromium_path) > 0:
        chrome_options.binary_location = chromium_path

    # Supress chrome logs
    # https://stackoverflow.com/questions/47392423/python-selenium-devtools-listening-on-ws-127-0-0-1
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # start chrome browser
    driver = webdriver.Chrome(options=chrome_options)
        #executable_path=chromedriver_binary,
    driver.get(url)

    soup = BeautifulSoup(driver.page_source.encode("utf-8"), "html.parser")
    logging.info("Web content: \n" + str(soup))
    driver.quit()

    return soup

def _check_coolmod_product(url: str, chromium_path: str) -> tuple[bool, float]:
    """Checks a Coolmod product page for availability and price.
    """
    price: float = float(0)
    available: bool = False

    soup: BeautifulSoup = _get_web_through_chromedriver(url, chromium_path)
    #response: requests.Response = requests.get(url)
    #soup = BeautifulSoup(response.text, "html.parser")

    div_group = soup.find("div", {"class": "product-details-prices"})

    if div_group is None:
        logging.warning("Product details group not found")
        return (False, 0.0)

    buy_button: Tag | None = div_group.find("span", {"class": "add-to-cart"})
    
    if buy_button is None:
        logging.warning("Product availability not found")
        return (False, 0.0)
    
    item: str
    for item in buy_button.strings:
        if "reserva" in item.lower():
            available = False
        elif "sin stock" in item.lower():
            available = False
        elif "añadir a la cesta" in item.lower():
            available = True

    main_price_element = div_group.find("span", {"class": "product_price int_price"})
    sup_price_element = div_group.find("span", {"class": "product_price_sup"})
    
    if main_price_element is None or sup_price_element is None:
        logging.warning("Price elements not found")
        return (available, 0.0)
    
    main_price: str = main_price_element.string # type: ignore
    sup_price: str = sup_price_element.string.replace(",", "").replace("€", "") # type: ignore

    price = float(main_price) + float(sup_price)/100

    return (available, price)

def _check_pccomp_product(url: str, chromium_path: str) -> tuple[bool, float]:
    """
    Sample `chromium_path`:
    C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\brave.exe
    """
    price: float = float(0)
    available: bool = False

    soup: BeautifulSoup = _get_web_through_chromedriver(url, chromium_path, slowcon=3)

    #from IPython import embed
    #embed()

    # TODO: check if the items are found and handle gracefully
    buy_button = None
    buy_buttons = soup.find_all("button")
    logging.error(f"Total buttons found: {len(buy_buttons)}")
    for button in buy_buttons:
        button_class = button.get("class")
        if button_class and any(cls.startswith("addToCartButton-") for cls in button_class):
            buy_button = button
            logging.error(f"Buy button found: {buy_button}")
            exit(1)
            break
        else:
            logging.error(f"Button class not found or doesn't match: {button_class}")
            exit(1)
    
    if buy_button is not None and buy_button.string is not None:
        available = "comprar" in buy_button.string.lower()
        logging.info(f"Availability: {buy_button.string.lower()}")

    full_price = soup.find("div", attrs={"class": "precioMain"})
    if full_price is not None:
        price = float(full_price['data-price']) # type: ignore

    return (available, price)

def _check_neobyte_product(url: str, chromium_path: str) -> tuple[bool, float]:
    """
    Sample `chromium_path`:
    C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\brave.exe
    """
    price: float = float(0)
    available: bool = False

    soup: BeautifulSoup = _get_web_through_chromedriver(url, chromium_path)

    # Get the div which contains the availability and price info
    group_div = soup.find("div", {"class": "product-prices"})

    if group_div is None:
        logging.warning("Product info group not found")
        return (False, 0.0)
    
    dom_available = group_div.find("span", {"id": "product-availability"})

    if dom_available is None:
        logging.warning("Availability element not found")
        return (False, 0.0)
    
    available_class = dom_available.get('class')
    available = available_class is not None and "badge-success" in available_class

    dom_price_element = group_div.find("span", {"class": "product-price"})
    if dom_price_element is None or dom_price_element.string is None:
        logging.warning("Price element not found")
        return (available, 0.0)
    
    dom_price = str(dom_price_element.attrs.get('content'))

    assert dom_price is not None, "Price not found, can't process it!"
    price = float(dom_price)

    return (available, price)

#######################################################################

class Product(TypedDict):
    url:      str
    group:    str
    platform: str
    currency: str
    price:    float
    minprice: float


class ProductLibrary:
    """Class that models the library containing all the products to be checked.
    """
    products: dict = {}

    @staticmethod
    def add_product(url: str, group: str) -> bool:
        """
        Returns:
        - A `bool` indicating if the insertion was accomplished (true)
        """
        result: bool = True

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
    def del_product(url: str, group: str) -> bool:
        """
        Returns:
        - A `bool` indicating if the removal was accomplished (true)
        """
        result: bool = True

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
    def check_products(chromium_path: str):
        """
        Runs the checks for all products in the library.
        """

        def run_check(check_function: FunctionType , product: str) -> tuple[bool, float]:
            availability, price = False, -1
            try:
                availability, price = check_function(product, chromium_path)
            except Exception as e:
                logging.warning(f"Error checking product {product}: {e}")

            return availability, price

        for group in ProductLibrary.products:

            logging.info(f"Group {group}")

            for product in ProductLibrary.products[group]:
                logging.info(f"Checking {product}")

                if "coolmod" in product.lower():
                    ProductLibrary.products[group][product] = \
                        run_check(_check_coolmod_product, product)

                elif "pccomponentes" in product.lower():
                    ProductLibrary.products[group][product] = \
                        run_check(_check_pccomp_product, product)

                elif "neobyte" in product.lower():
                    ProductLibrary.products[group][product] = \
                        run_check(_check_neobyte_product, product)

                else:
                    logging.warning("Webpage not supported!")
