# @name         Product Scraper
# @version      6.0
# @description  collects data from categories on website.
# @author       Ciaran Byrne

import bs4
import requests
import csv
import pandas as pd  
import os
import sys

from termcolor import colored
from bs4 import BeautifulSoup
from time import sleep
from os.path import exists

from selenium import webdriver
from selenium.webdriver.common.by import By 

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from win10toast import ToastNotifier


# event listener to check whether the price has been changed or not, checks the stock when a user wants to go to it;
# count of products scraped


# clean up code

# the output file needs to be the updated name ? then if the updated name doesn't work, then do it??? idk
# just add the dirUpdated statement to the pd output code

class Scrape:
    def checkTitle(self, title):
        # ******************* checking for special characters  ******************* #
        special_characters = '[{!@#$%£^&*()-_=+\|]}[{;:/?.>,<}]"'

        if any(s in special_characters for s in title):
            return True
        else:
            return False   
            
    def __init__(self):
        user = "Info@rdwrightwc.co.uk"
        pw = "Onhold"

        signedIn = True
        googleOpen = True

        # ******************* Setting global variables ******************* #
        global toaster
        toaster = ToastNotifier()
        global dontCarryOn 
        dontCarryOn= False

        with open("categories.txt","r") as f: # reading categories
            categories = f.readlines()
        with open("categories.txt","r") as f:
            catCount = sum(1 for line in f)
 
        print(" ")
        print(colored(f"Scraping {catCount} categories","green"))
        print(" ")

        # ******************* User arguments ******************* #
        args = sys.argv[1:]

        if "-help" in args:
            print("open google: -g, -google")
            print("sign in to program: -s, -signin")
            quit()
        else: None
        
        if "-signin" in args: # if user is wanting to sign in
            signedIn = False 
        else: None

        if "-google" in args: # if user is wanting to open google
            googleOpen = False 
        else: None 

        if googleOpen: None #if google is already open or not
        else:
            print("opening google")
            os.system("start cmd /k chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\TEGchrome")
            sleep(1)
            print("closing cmd")
            os.system("taskkill /f /im cmd.exe")

        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:9222")
        # ser = Service("C:\\Users\\Student\\OneDrive\\Desktop\\coding\\chromedriver.exe")
        # self.driver = webdriver.Chrome(service=ser, options=options)
        self.driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
        self.driver.implicitly_wait(10)

        if signedIn: # if user is signed in 
            None
        else:
            print(colored("Logging in...","green"))
            self.driver.get("https://www.gspen.co.uk/customer/account/login")
            sleep(1)
            self.driver.find_element(By.NAME, "login[username]").send_keys(user) # sending username
            sleep(0.5)
            self.driver.find_element(By.NAME, "login[password]").send_keys(pw) # sending password
            sleep(0.5)
            self.driver.find_element(By.XPATH, "/html/body/div[2]/main/div[2]/div/div[3]/div/form/fieldset/div[4]/button/span") # clicking submit
            print(colored("Successfully logged in","green"))

        # ******************* Scraping categories from categories.txt ******************* #
        for url in categories:
            try:
                self.driver.get(url) # going to category 
                html = self.driver.page_source # getting current page source
                soup = BeautifulSoup(html, features="html.parser")

                catTitle = soup.find('h1', {'class':'page-title'}) # getting page title and making it a folder
                main_dir = catTitle.text.strip()

            except Exception as e: # if url is invalid
                print(colored(f"Couldn't fetch {url}","red"))
                print(colored("ERROR:","red"))
                print(colored(f"{e}","red"))
                continue

            titleOkay = self.checkTitle(main_dir) # checking if title is okay to use, if not changing it
            if titleOkay:
                print(colored(f"{main_dir}", "red"))
                main_dir = ''.join(e for e in main_dir if e.isalnum())
                print(colored(f"Updated: {main_dir}","green"))
            else: None

            main_dir = f"upload/{main_dir}" # changing path to upload folder
            if os.path.isdir(f"{main_dir}"): # checking if path already exists, if not building it
                print(" ")
                print(colored(f"{main_dir} already exists","red"))
                print(" ")
            else:
                os.mkdir(main_dir,mode = 0o666) 
                print(colored("Main directory '% s' built" % main_dir, "green"))

            href_list = []
            cards = soup.find_all("a", attrs={"class":"card__link"})    
            for card in cards:
                get_href = card["href"]
                href_list.append(get_href) # getting all the card links
            self.hrefs(href_list, main_dir)

    
    def hrefs(self, href_list, main_dir):
        # ******************* Going into first cards and collecting second card titles ******************* #
        for url in href_list:
            a = requests.get(url)
            s = bs4.BeautifulSoup(a.text, features="html.parser")
            title = s.find('h1', {'class':'page-title'})
            sub_dir = title.text.strip()

            titleOkay = self.checkTitle(sub_dir) # checking if title is okay
            if titleOkay:
                print(colored(f"{sub_dir}", "red"))
                print("Special characters")
                sub_dir = ''.join(e for e in sub_dir if e.isalnum())
                print(colored(f"updated: {sub_dir}","green"))
            else: None
            if os.path.isdir(f"{main_dir}/{sub_dir}"):
                print(" ")
                print(colored(f"{main_dir}/{sub_dir} already exists","red"))
                print(" ")
            else:
                os.mkdir(f"{main_dir}/{sub_dir}") 
                print(colored("Sub directory '% s' built" % sub_dir, "green"))

            card_links = s.find_all("a", {"class":"card__link"}) # for every product in card link
            for link in card_links:
                href = link["href"]
                # print(colored(f"Link: {href}","blue"))
                self.scrape(href, main_dir, sub_dir)
                
    def scrape(self, href, main_dir, sub_dir):
        global dirUpdated
        global spreadsheetCount
        global productCount 
        dirUpdated = False
        spreadsheetCount = 0
        productCount = 0

        print(colored(f"Fetching {href}","blue"))
        self.driver.get(href)
        html = self.driver.page_source # getting current page source
        soup = BeautifulSoup(html, features="html.parser")
        t = soup.find('h1', {'class':'page-title'}) # getting title and saving it as a sub directory
        print(colored(f"title: {t.text}","blue"))
        subsub_dir = t.text.strip()
        titleOkay = self.checkTitle(subsub_dir)
        if titleOkay:
            print(colored(f"{subsub_dir}", "red"))
            subsub_dir = ''.join(e for e in subsub_dir if e.isalnum())
            print(colored(f"Updated: {subsub_dir}","green"))
        else: None

        if os.path.isdir(f"{main_dir}/{sub_dir}/{subsub_dir}"):
            print(colored(f"{main_dir}/{sub_dir}/{subsub_dir} already exists","red"))
            dontCarryOn = True
        else:
            try:
                os.mkdir(f"{main_dir}/{sub_dir}/{subsub_dir}")
                print(colored("Nested directory '% s' built" % subsub_dir, "green"))
                dontCarryOn = False
            except:
                toaster.show_toast("Naming error",
                                "See program.",
                                icon_path=None,
                                duration=5)
                print(colored(f"Couldn't build {subsub_dir}","red"))
                subsub_dir = input("Enter name for directory: ")
                dirUpdated = True
        
        if dontCarryOn: None
        else:
            try:
                details = soup.find_all("a", attrs={"class":"grid-link"})
                # srcs = soup.find_all("img", attrs={"class":"grid-image"})
            except:
                print(colored("Something went wrong finding product information", "red"))
                print(colored("Are you on a category?", "blue"))
            
            try:
                prices = soup.find_all("span", attrs={"class":"special-price"})
            except:
                print(colored("Couldn't find prices of products", "red"))
                print(colored("Are you logged in?", "blue"))
            
            try:
                title = soup.find('h1', {'class':'page-title'})
                print(title.text)
                category = title.text
            except:
                print(colored("Couldn't find category name","red"))
                category = "Untitled"

            href_list = []
            title_list = []
            price_list = []

            # ******************* Searching through classes to find product data ******************* #
            for i in details:
                get_href = i["href"]
                href_list.append(get_href)
                title_list.append(i.text)

            for p in prices:
                p = p.text
                x = p.replace("Special Price", " ")
                y = x.replace("£"," ")
                price_list.append(y.strip())
            
            if not price_list:
                print(colored("Couldn't get prices","red"))
                print(colored("Make sure you're on a category","blue"))
            else:
                None

            # checking spreaadsheet name is okay
            spreadsheetCount = 0
            print(" ")
            print(colored("Making spreadsheet..","green"))
            spreadsheet_name = f"{category}"

            special_characters = '[{!@#$%£^&*()-_=+\|]}[{;:/?.>,<}]"'

            if any(s in special_characters for s in category):
                category = ''.join(e for e in category if e.isalnum())
                spreadsheet_name = f"{category}"
            else:
                None

            if dirUpdated: # if there has been an error with the original name
                spreadsheet_name = subsub_dir
            else:
                None

            # ******************* Checking if spreadsheet already exists  ******************* #
            pwd = os.getcwd()
            path = pwd + f"\\bin\\{spreadsheet_name}"
            doessExist = os.path.exists(path)
            if doessExist:
                print(colored(f"Spreadsheet {spreadsheet_name} already exists", "blue"))
                print(" ")
                while spreadsheetCount < 5:
                    spreadsheet_name = f"{category}{spreadsheetCount}"
                    if exists(spreadsheet_name):
                        spreadsheetCount += 1
                    else:
                        print(colored(f"Creating {spreadsheet_name}", "green"))
                        spreadsheetCount = 6
            else:
                print(colored(f"Creating {spreadsheet_name}", "green"))
            spreadsheet_name.strip()

            vendor = "TEG"
            type = " "
            updatedDir = main_dir.replace('upload/', ' ') # removing upload/ from string
            tags = f"{updatedDir}, {sub_dir}, {subsub_dir}" # adding tags of the main directories
            option1 = "Title"
            option1value = "Default Title"
            variantgrams = "0"
            inventory = "shopify"
            qty = "999"
            policy = "deny"
            fulfill = "manual"
            shipping = "TRUE"
            taxable = "TRUE"
            barcode = " "
            published = "TRUE"
            discount = None
            manual = True
            compareAtPrice = " "
            
            # ******************* Creating spreadsheet in folder 'bin'  ******************* #
            with open(f'bin/{spreadsheet_name}', mode='w') as employee_file:

                employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                employee_writer.writerow(['Handle'] + ['Title'] + ['Body (HTML)'] + ['Vendor'] + ['Type'] + ['Tags'] + ['Published'] + ['Option1 Name'] + ['Option1 Value'] + ['Variant Grams'] + ['Variant Inventory Tracker'] + ['Variant Inventory Qty'] + ['Variant Inventory Policy'] + ['Variant Fulfillment Service'] + ['Variant Price'] + ['Variant Compare At Price'] + ['Variant Requires Shipping'] + ['Variant Taxable'] + ['Variant Barcode'] + ['Image Src'])
                for i in title:
                    productCount += 1
                    
                for title, url, price in zip(title_list, href_list, price_list):
                    print(colored(f"{title}","green"))
                    # print(url)
                    if "," in price: # if price contains a comma
                        price = price.replace(',', '')
                        price = float(price)
                    else:
                        price = float(price)

                    print("Old price:",price)
                    percent = price/100*45 # 45% of price
                    price = price + percent # adding percentage back to price
                    price = format(price, '.2f')
                    price = float(price)
                    print("Updated price:",price)    

                    handle = "-".join(title.split()).lower() # formatting the titles for the shopify handle

                    a = requests.get(url)
                    soup = BeautifulSoup(a.text, features="html.parser")
                
                    d = soup.find('div', {'class':'product__accordion-content-inner'})
                    desc = d.text # description
                    # print(desc)
                    print(colored("Collected description","green"))


                    table = soup.find('table', {'class':'product__techspec'})
                    # print(table)
                    print(colored("Collected table","green"))
    
                    final = str(desc) + "<br>" + "<br>" + str(table)
                    all_images = []
                    count = 0
                    newcount = 1
                    product_images = soup.find_all('a', {'class':'gallery__thumb-link'})
                    for i in product_images:
                        get_href = i["href"]
                        all_images.append(get_href)
                        print(colored(f"{get_href}","green"))
                        count += 1
                    # if it has more than one product image display it separately
                    if count > 1:
                        employee_writer.writerow([f'{handle}'] + [f'{title}'] + [f'{final}'] + [f'{vendor}'] + [f'{type}'] + [f'{tags}'] + [f'{published}'] + [f'{option1}'] + [f'{option1value}'] + [f'{variantgrams}'] + [f'{inventory}'] + [f'{qty}'] + [f'{policy}'] + [f'{fulfill}'] + [f'{price}'] + [f'{compareAtPrice}'] + [f'{shipping}'] + [f'{taxable}'] + [f'{barcode}'])
                        for image in all_images:
                            employee_writer.writerow([f'{handle}'] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [f'{image}'])
                    else:
                        employee_writer.writerow([f'{handle}'] + [f'{title}'] + [f'{final}'] + [f'{vendor}'] + [f'{type}'] + [f'{tags}'] + [f'{published}'] + [f'{option1}'] + [f'{option1value}'] + [f'{variantgrams}'] + [f'{inventory}'] + [f'{qty}'] + [f'{policy}'] + [f'{fulfill}'] + [f'{price}'] + [f'{compareAtPrice}'] + [f'{shipping}'] + [f'{taxable}'] + [f'{barcode}'] + [f'{get_href}'])

            # ******************* removing whitespace in csv ******************* #
            df = pd.read_csv(f'bin/{spreadsheet_name}', encoding = 'unicode_escape')
            output_name = spreadsheet_name + "_output.csv"
            output_name.strip()
            df.to_csv(f'{main_dir}/{sub_dir}/{subsub_dir}/{output_name}', index=False)
    
    def checkEmptyFolders(self):
        # ******************* Checking for empty folders and making an error log ******************* #
        directory = "upload"
        all = [x[0] for x in os.walk(directory)]
        empty_dirs = []
        for i in all:
            if len(os.listdir(i) ) == 0:
                empty_dirs.append(i)
            else: None

        print(" ")
        with open("errors.txt", "a") as f: # saving empty directories to errors.txt
            for i in empty_dirs:
                f.write(f"{i}\n")
                print(colored(i,"red"))

        
Scrape()