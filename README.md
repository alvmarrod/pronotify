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

## Versions

Current version tag is available in [version.txt](./version.txt) file, and you can refer to the [changelog](./changelog.md) file for more information on each version number.

Remember that a new commit does not imply a new version.

## Dependencies

- [requests](https://pypi.org/project/requests/)
- [bs4](https://pypi.org/project/bs4/)
- [emoji](https://pypi.org/project/emoji/)

To install all these requirements, you can execute:

```
python -m pip install -r requirements.txt
```