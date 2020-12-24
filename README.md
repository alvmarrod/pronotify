# pronotify

This project aims to monitor required products from different webpages, and show if those products are available or not.

## Usage

Execute the main script to access the app main menu and start working from there.

```
$ python main.py

############## pronotify ##############
####                               ####
# 1. Add product                      #
# 2. Remove product                   #
# 3. Show status                      #
# 4. Exit                             #
####                               ####
#######################################

Choose an option:
```

There are some vendors that require the usage of a web browser to renderize several items with JavaScript, e.g. *pccomponentes*. If you're not going to use them, you don't need to worry about the following point.

By default, as web browser it will be used Chrome, but if you don't have Chrome web browser installed, you can target a different **Chromium web browser** to be used.

```
$ python main.py --chromium "C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
```

## Supported vendors

- [Coolmod](http://coolmod.com/) - Spanish language
- [PCComponentes](https://www.pccomponentes.com/) - All languages - Requires ChromeDriver!

## Versions

Current version tag is available in [version.txt](./version.txt) file, and you can refer to the [changelog](./changelog.md) file for more information on each version number.

Remember that a new commit does not imply a new version.

## Dependencies

- [requests](https://pypi.org/project/requests/)
- [bs4](https://pypi.org/project/bs4/)
- [selenium](https://pypi.org/project/selenium/)
- [emoji](https://pypi.org/project/emoji/)

To install all these requirements, you can execute:

```
python -m pip install -r requirements.txt
```

### ChromeDriver

Some webpages need to renderize further HTML Changes by JavaScript actions before scraping them. It puts us in the need of loading the webpages in the same way a browser would do it, so we actually need a web browser to work for us.

Our choice is [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/getting-started), that should be installed beforehand in your computer.

You should install the appropriate chromedriver from their [downloads section](https://sites.google.com/a/chromium.org/chromedriver/downloads).

