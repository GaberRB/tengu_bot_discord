import json
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
import pyshorteners
import re
from random import randrange


class MontaPC:
    pc = []
    LISTA = 'pcs.json'

    def lerComponentes():
        file = open(f'PCS/{str(randrange(start=0, stop=37))}.json', encoding='utf-8')
        data = json.load(file)
        file.close()
        return data





