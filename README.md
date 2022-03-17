# Pandoc/python static site generator

The best of python, pandoc (haskell) and shell all in one. Should work with a standard full python installation without requiring `pip install`. Made for ease of use and development due to python's built in string manipulation functions. Pandoc and python are widely used hopefully lending to the longevity of this code.

## Usage

```bash
./gen.py build # Compiles markdown files in directory named "src" to html in "site" directory.
./gen.py upload # Uploads to ssh named my_server with target directory /var/www/html
./gen.py git # commits and pushes to git
./gen.py all # Does all of the above
./gen.py serve # Creates a local server for testing
```

Store assets in `./assets` directory these will be copied over to `src/assets/`.

## Features
- RSS feed generated with item for each page.
- 1 folder deep folder structure is transformed into categorised pages. See example below.
- Write pages in pandoc markdown.

## Requirements
- Python3.\*
- A Linux shell (maybe POSIX (untested)). Tested on ubuntu and ubuntu for WSL. Should work on most Linux distros.
- Pandoc. `sudo apt install pandoc` if debian based.

Should work on macos if pandoc execuable is available. NOT TESTED.

## Example setup

For example create directory of directories with this structure. Each post can be put within a folder which is it's category. The generator will then simply create an index of each post within each category and display this as a list.
```
./gen.py build
# Here is an example src directory. The home page is the index.md file.

src
├── index.md
├── about.md
├── art
│   └── artist_page.md
└── maths
    └── my_favourite_maths.md

```

Each markdown must contain the following at the top of the file, with at least the title value:

```
---
lang: en-GB
title: Title for page
description: Some description
tags: ["example","another","climate crisis"]

---
```
