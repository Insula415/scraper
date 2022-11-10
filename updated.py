# @name         Product Scraper
# @version      5.0
# @description  collects data from categories on website.
# @author       Ciaran Byrne


import bs4
from numpy import signedinteger
import requests
import keyboard
import csv
import pandas as pd  
import os
import subprocess

from termcolor import colored
from bs4 import BeautifulSoup
from time import sleep
from os.path import exists

from selenium import webdriver
from selenium.webdriver.common.by import By 

from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


# Handle
# Title
# Body (HTML)
# Vendor
# Type
# Tags
# Published
# Option1 Name
# Option1 Value
# Variant Grams
# Variant Inventory Tracker
# Variant Inventory Qty	
# Variant Inventory Policy	
# Variant Fulfillment Service	
# Variant Price	
# Variant Compare At Price	
# Variant Requires Shipping	
# Variant Taxable
# ariant Barcode	
# Image Src

# will also need to add chrome to path

class Scrape:
    def __init__(self):
        global path
        global newpath
        try:
            with open("chrome.txt", "r") as f:
                newpath = f.readlines()
        except:
            print("Something went wrong fetching path")
            print("Have you ran setup.py?")
            quit()
        path = ''.join(newpath)
        path = str(path)

        user = "Info@rdwrightwc.co.uk"
        pw = "Onhold"
        print(" ")
        print(colored("Getting user options", "green"))
        savedopts = path + "/saved_options.txt"
        if os.path.exists(f"{savedopts}"):
            with open(f"{savedopts}", "r") as f:
                print("PATH EXISTS")
                lines = f.readlines()
                if lines[0].strip() == "true":
                    signedIn = True
                    print("Already signed in")
                else:
                    signedIn = False
                    print("Not signed in")
                if lines[1].strip() == "Manual":
                    print("Manual")
                    amount = " "
                    print("Manually adding prices")
                elif lines[1].strip() == "Multiply":
                    print("Multiply")
                    multi = lines[2].strip()
                    add = None
                    print("Multiplying prices by",multi)
                elif lines[1].strip() == "Add":
                    multi = None
                    add = lines[2].strip()
                    print("Adding prices by",add)
                if lines[3].strip() == "0":
                    discount = None
                    print("No discount")
                else:
                    discount = lines[3].strip()
                    print("Discount:",discount)

                if lines[4].strip() == "TRUE":
                    published = "TRUE"
                    print("Publish products")
                else:
                    published = "FALSE" 
                    print("Don't publish products")
        else:
            opts = path + "/options.txt"
            with open(f"{opts}", "r") as f:
                lines = f.readlines()
                if lines[0].strip() == "true":
                    signedIn = True
                    print("Already signed in")
                else:
                    signedIn = False
                    print("Not signed in")
                if lines[1].strip() == "Manual":
                    print("Manual")
                    amount = " "
                    print("Manually adding prices")
                elif lines[1].strip() == "Multiply":
                    print("Multiply")
                    multi = lines[2].strip()
                    add = None
                    print("Multiplying prices by",multi)
                elif lines[1].strip() == "Add":
                    multi = None
                    add = lines[2].strip()
                    print("Adding prices by",add)
                if lines[3].strip() == "0":
                    discount = None
                    print("No discount")
                else:
                    discount = lines[3].strip()
                    print("Discount:",discount)

                if lines[4].strip() == "TRUE":
                    published = "TRUE"
                    print("Publish products")
                else:
                    published = "FALSE" 
                    print("Don't publish products")
        print(" ")

        
          
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:9222")

        self.driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
        self.driver.implicitly_wait(10)
        
        run = path + "/runagain.txt"
        if os.path.exists(f"{run}"): #if user chooses run again
            None
            signedIn = False
        elif signedIn:
            self.driver.get("https://www.gspen.co.uk/")
        else:
            print(colored("LOGGING IN","blue"))
            self.driver.get("https://www.gspen.co.uk/customer/account/login")
            sleep(1)
            self.driver.find_element(By.NAME, "login[username]").send_keys(user)
            sleep(1)
            self.driver.find_element(By.NAME, "login[password]").send_keys(pw)
            sleep(1)
            self.driver.find_element(By.NAME, "send").click()
 
        running = True
        while running:
            cat = input("Enter category name (no special characters except &) or press E to leave: ")
            
            if cat.lower() == "e":
                print("EXITING")
                running = False
                quit()
            else:
                tags = input("Tags: ")
                html = self.driver.page_source # getting current page source
                soup = BeautifulSoup(html, features="html.parser")

                try:
                    details = soup.find_all("a", attrs={"class":"grid-link"})
                    srcs = soup.find_all("img", attrs={"class":"grid-image"})
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

                #searching through classes
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

                special_characters = '"!@#$%^*()-+?_=,<>/"'

                if any(s in special_characters for s in category):
                    category = cat
                    spreadsheet_name = f"{category}"
                else:
                    None

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

                vendor = "TEG"
                type = " "
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
                productCount = 0

                with open(f'bin/{spreadsheet_name}', mode='w') as employee_file:

                    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    employee_writer.writerow(['Handle'] + ['Title'] + ['Body (HTML)'] + ['Vendor'] + ['Type'] + ['Tags'] + ['Published'] + ['Option1 Name'] + ['Option1 Value'] + ['Variant Grams'] + ['Variant Inventory Tracker'] + ['Variant Inventory Qty'] + ['Variant Inventory Policy'] + ['Variant Fulfillment Service'] + ['Variant Price'] + ['Variant Compare At Price'] + ['Variant Requires Shipping'] + ['Variant Taxable'] + ['Variant Barcode'] + ['Image Src'])

                    for title, url, price in zip(title_list, href_list, price_list):
                        # print(title)
                        # print(url)
                        # print(price)
                        price = float(price)
                            
                        if multi:
                            price = price * int(multi)
                            # print("Updated:",price)
                        elif add:
                            price = price + int(add)
                            # print("Updated:",price)
                        else:
                            None     
                        
                        # adding discount
                        if discount:
                            dis = price * float(discount) / 100
                            final = dis + price
                            compareAtPrice = "{:.2f}".format(final)
                            # print("Reduced from:",compareAtPrice) 
                        else:
                            compareAtPrice = " "         

                        handle = "-".join(title.split()).lower()

                        a = requests.get(url)
                        soup = BeautifulSoup(a.text, features="html.parser")
                    
                        d = soup.find('div', {'class':'product__accordion-content-inner'})
                        desc = d.text # description
                        # print(desc)

                        table = soup.find('table', {'class':'product__techspec'})
                        # print(table)
                        # fdes = des.text # table

                        # desc_list = []

                        # for i,k in zip(fdes[0::2], fdes[1::2]):
                        #     desc_list.append(i,k)

                        final = str(desc) + "<br>" + "<br>" + str(table)
                        # str(line[column]) + '\t'
                        all_images = []
                        count = 0
                        newcount = 1
                        product_images = soup.find_all('a', {'class':'gallery__thumb-link'})
                        for i in product_images:
                            get_href = i["href"]
                            all_images.append(get_href)
                            # print(get_href)
                            count += 1
                        # if it has more than one product image display it separately
                        if count > 1:
                            employee_writer.writerow([f'{handle}'] + [f'{title}'] + [f'{final}'] + [f'{vendor}'] + [f'{type}'] + [f'{tags}'] + [f'{published}'] + [f'{option1}'] + [f'{option1value}'] + [f'{variantgrams}'] + [f'{inventory}'] + [f'{qty}'] + [f'{policy}'] + [f'{fulfill}'] + [f'{price}'] + [f'{compareAtPrice}'] + [f'{shipping}'] + [f'{taxable}'] + [f'{barcode}'])
                            for image in all_images:
                                employee_writer.writerow([f'{handle}'] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [f'{image}'])
                        else:
                            employee_writer.writerow([f'{handle}'] + [f'{title}'] + [f'{final}'] + [f'{vendor}'] + [f'{type}'] + [f'{tags}'] + [f'{published}'] + [f'{option1}'] + [f'{option1value}'] + [f'{variantgrams}'] + [f'{inventory}'] + [f'{qty}'] + [f'{policy}'] + [f'{fulfill}'] + [f'{price}'] + [f'{compareAtPrice}'] + [f'{shipping}'] + [f'{taxable}'] + [f'{barcode}'] + [f'{get_href}'])

                        productCount += 1
                # geting rid of empty lines in csv
                df = pd.read_csv(f'bin/{spreadsheet_name}', encoding = 'unicode_escape')
                output_name = spreadsheet_name + "_output.csv"
                df.to_csv(f'upload/{output_name}', index=False)
                print("Products:",productCount)
                print(colored(f"Saved as {output_name}", "green"))
        

Scrape()