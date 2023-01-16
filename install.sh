#!/usr/bin/env bash

# install dependencies
sudo apt install -y tesseract-ocr poppler-utils libxext-dev libsm-dev libxrender-dev

# create virtual environment
virtualenv env -p python3.8
source env/bin/activate

pip install -U setuptools
pip install .
