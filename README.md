# Pandoc/python static site generator

The best of python, pandoc (haskell) and shell all in one. Should work with a standard full python installtion without requiring `pip install`.


## Requirements
- Python3.\*
- A Linux shell. Tested on ubuntu and ubuntu for WSL. Should work on most Linux distros.
- Pandoc. `sudo apt install pandoc` if debian based.

## Example setup

For example create directory of directories with this structure. Each post can be put within a folder which is it's category. The generator will then simply create an index of each post within each category and display this as a list.
```
python3 gen.py build
.
├── index.md
└── src
    ├── art
    │   └── text.md
    ├── philosophy
    │   ├── text.md
    │   └── text2.md
    └── science
        ├── text1.md
...
```

Each markdown must contain the following at the top of the file:

```
---
lang: en-GB
title: Title for page
description: Some description
tag: ["religion","climate"]

---
```

### Potentially useful notes

Convert all newlines into \n: `awk '$1=$1' ORS='\\n' file`

Find and replace on one line only in vim: `:s/str1/str2/g`

#### Old notes
```
pandoc --verbose -s --toc --toc-depth 2 -f markdown -t html index.md > src/main.html
cat src/base.html src/main.html src/foot.html > site/index.html

categories=($(ls -d src/*/))
for fldr in ${categories[@]}; do
    eval 'ls "$fldr"'
done
```



