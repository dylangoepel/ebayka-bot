import requests
import sys
import os
from random import randint
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def parseKeywords(path):
    with open(path, "r") as f:
        text = f.read()
    entries = [t.split("\n") for t in text.split("\n\n")]
    data = []
    for entry in entries:
        data.append((entry[0].strip("\n"), "".join(entry[1:])))
    return data

class EbayClient:
    def __init__(self):
        options = Options()
        options.add_argument("disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)
        driver.get('https://www.ebay-kleinanzeigen.de/m-einloggen.html')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'my-manageads-content'))).click()
        self.driver = driver
        self.contacts = self.contacted()

    def randomWait(self, a, b):
        sleep(randint(a, b) / 1000)

    def simulateTyping(self, elem, text):
        for c in text:
            elem.send_keys(c)
            self.randomWait(10, 70)

    def contacted(self):
        self.driver.get('https://www.ebay-kleinanzeigen.de/m-nachrichten.html')
        self.randomWait(500, 700)
        parser = BeautifulSoup(self.driver.page_source)
        return [t.text for t in parser.find_all('h2', {"class": "conversationitem-title"})]

    def _search(self, query):
        self.randomWait(1000, 1200)
        searchBar = self.driver.find_element_by_xpath('//*[@id="site-search-query"]')
        searchBar.clear()
        self.simulateTyping(searchBar, query)
        self.randomWait(100, 800)
        searchButton = self.driver.find_element_by_xpath('//*[@id="site-search-submit"]')
        searchButton.click()

    def search(self, query):
        terms = query.split(" ") 
        searchTerms = list(filter(lambda x: x[0] != "-", terms))
        dropTerms   = list(filter(lambda x: x[0] == "-", terms))
        self._search(" ".join(searchTerms))
        parser = BeautifulSoup(self.driver.page_source)
        ads = {}
        for link in parser.find_all("a", {"class": "ellipsis"}):
            if any([t.lower() in link.get_text().lower() for t in dropTerms]):
                continue
            ads[link.get_text()] = "https://www.ebay-kleinanzeigen.de" + link["href"]
        return ads

    def apply(self, ad, name, text):
        if name in self.contacts:
            pass

        self.driver.get(ad)
        self.randomWait(2000, 2500)
        messagearea = self.driver.find_element_by_xpath('//*[@id="viewad-contact-form"]/fieldset/div[1]/div/textarea')
        self.simulateTyping(messagearea, text)
        namefield = self.driver.find_element_by_xpath('//*[@id="viewad-contact-form"]/fieldset/div[2]/div/input')
        self.randomWait(100, 400)
        namefield.clear()
        self.simulateTyping(namefield, name)
        submit = self.driver.find_element_by_xpath('//*[@id="viewad-contact-form"]/fieldset/div[4]/div/button')
        submit.click()

    def applyAll(self, terms, name, text):
        ads = self.search(terms)
        for ad in ads:
            try:
                self.apply(ads[ad], name, text)
                self.randomWait(2000, 5000)
            except:
                pass


if len(sys.argv) != 3:
    print("Invalid Usage")
    sys.exit(1)

name = sys.argv[1]
kwpath = sys.argv[2]

client = EbayClient()
keywords = parseKeywords(kwpath)
for entry in keywords:
    client.applyAll(entry[0], name, entry[1])
