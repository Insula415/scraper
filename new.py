# @name         Product Scraper
# @version      5.0
# @description  collects data from categories on website.
# @author       Ciaran Byrne

# test comment
import bs4
from numpy import signedinteger
import requests
import keyboard
import csv
import pandas as pd  
import os
import re
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

# will also need to add chrome to path

# add arguments to open google and shit
# need to add try and except on everything
# also need to make sure special characters aren't in folder names

class Scrape:

    def __init__(self):
        user = "Info@rdwrightwc.co.uk"
        pw = "Onhold"

        signedIn = True
        
        with open("main.txt","r") as f:
            categories = f.readlines()
        # print("opening google")
        # os.system("start cmd /k chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\TEGchrome")
        # sleep(0.3)
        # print("closing cmd")
        # os.system("taskkill /f /im cmd.exe")

        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:9222")
        ser = Service("C:\\Users\\Student\\OneDrive\\Desktop\\coding\\chromedriver.exe")
        self.driver = webdriver.Chrome(service=ser, options=options)
        # self.driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
        self.driver.implicitly_wait(10)

        for url in categories:
            self.driver.get(url) # going to category
            html = self.driver.page_source # getting current page source
            soup = BeautifulSoup(html, features="html.parser")

            catTitle = soup.find('h1', {'class':'page-title'}) # getting page title and making it a folder
            main_dir = catTitle.text.strip()

            os.mkdir(main_dir,mode = 0o666) 
            print("Main directory '% s' built" % main_dir)

            # div card__item -> a href
            href_list = []
            cards = soup.find_all("a", attrs={"class":"card__link"})    
            for card in cards:
                get_href = card["href"]
                href_list.append(get_href) # getting all the card links
            self.hrefs(href_list, main_dir)
            
    def hrefs(self, href_list, main_dir):
        print("hrefs function called")
        # print(href_list)
        for url in href_list:
            a = requests.get(url)
            s = bs4.BeautifulSoup(a.text, features="html.parser")
            title = s.find('h1', {'class':'page-title'})
            print(title.text)
            sub_dir = title.text.strip()
            os.mkdir(f"{main_dir}/{sub_dir}")
            print(colored("Sub directory '% s' built" % sub_dir, "green"))
            card_links = s.find_all("a", {"class":"card__link"})
            for link in card_links:
                href = link["href"]
                print(colored(f"Link:{href}","blue"))
                self.scrape(href, main_dir, sub_dir)
                
                # print(link.text)
            # for link in card_links:
            #     href = link["href"]
            #     b = requests.get(href)
            #     c = bs4.BeautifulSoup(b.text, features="html.parser")
            #     t = c.find('h1', {'class':'page-title'})
            #     print("Sub category title:",title.text)
                # with open(f"{sub_dir}/{href}.txt", "w") as f:
                #     f.write("test")
                #     f.close()
                
    def scrape(self, href, main_dir, sub_dir):
        print(colored(f"Fetching {href}","blue"))
        b = requests.get(href)
        c = bs4.BeautifulSoup(b.text, features="html.parser")
        t = c.find('h1', {'class':'page-title'})
        print(colored(f"title:{t.text}","blue"))
        subsub_dir = t.text.strip()
        os.mkdir(f"{main_dir}/{sub_dir}/{subsub_dir}")
        print(colored("Nested directory '% s' built" % subsub_dir, "green"))

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
            quit()
        else:
            None

        # checking spreaadsheet name is okay
        spreadsheetCount = 0
        print(" ")
        print(colored("Making spreadsheet..","green"))
        spreadsheet_name = f"{category}"

        special_characters = '"!@#$%^&*()-+?_=,<>/"'

        if any(s in special_characters for s in category):
            re.sub('[^A-Za-z0-9]+', '', category)
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
        tags = " "
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

        for title, url, price in zip(title_list, href_list, price_list):
            print(title)
            print(url)
            print(price)
            sleep(5)
        quit()
        with open(f'bin/{spreadsheet_name}', mode='w') as employee_file:

            employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            employee_writer.writerow(['Handle'] + ['Title'] + ['Body (HTML)'] + ['Vendor'] + ['Type'] + ['Tags'] + ['Published'] + ['Option1 Name'] + ['Option1 Value'] + ['Variant Grams'] + ['Variant Inventory Tracker'] + ['Variant Inventory Qty'] + ['Variant Inventory Policy'] + ['Variant Fulfillment Service'] + ['Variant Price'] + ['Variant Compare At Price'] + ['Variant Requires Shipping'] + ['Variant Taxable'] + ['Variant Barcode'] + ['Image Src'])

            for title, url, price in zip(title_list, href_list, price_list):
                print(title)
                print(url)
                # print(price)
                price = float(price)
                price = format(price, '.2f')
                price = float(price)
                print("Old price:",price)
                percent = price/100*45 # 45% of price
                price = price + percent # adding percentage back to price
                price = float(price)
                price = format(price, '.2f')
                price = float(price)
                print("Updated price:",price)    

                handle = "-".join(title.split()).lower()

                a = requests.get(url)
                soup = BeautifulSoup(a.text, features="html.parser")
            
                d = soup.find('div', {'class':'product__accordion-content-inner'})
                desc = d.text # description
                print(desc)

                table = soup.find('table', {'class':'product__techspec'})
                print(table)
  
                final = str(desc) + "<br>" + "<br>" + str(table)
                all_images = []
                count = 0
                newcount = 1
                product_images = soup.find_all('a', {'class':'gallery__thumb-link'})
                for i in product_images:
                    get_href = i["href"]
                    all_images.append(get_href)
                    print(get_href)
                    count += 1
                # if it has more than one product image display it separately
                if count > 1:
                    employee_writer.writerow([f'{handle}'] + [f'{title}'] + [f'{final}'] + [f'{vendor}'] + [f'{type}'] + [f'{tags}'] + [f'{published}'] + [f'{option1}'] + [f'{option1value}'] + [f'{variantgrams}'] + [f'{inventory}'] + [f'{qty}'] + [f'{policy}'] + [f'{fulfill}'] + [f'{price}'] + [f'{compareAtPrice}'] + [f'{shipping}'] + [f'{taxable}'] + [f'{barcode}'])
                    for image in all_images:
                        employee_writer.writerow([f'{handle}'] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [f'{image}'])
                else:
                    employee_writer.writerow([f'{handle}'] + [f'{title}'] + [f'{final}'] + [f'{vendor}'] + [f'{type}'] + [f'{tags}'] + [f'{published}'] + [f'{option1}'] + [f'{option1value}'] + [f'{variantgrams}'] + [f'{inventory}'] + [f'{qty}'] + [f'{policy}'] + [f'{fulfill}'] + [f'{price}'] + [f'{compareAtPrice}'] + [f'{shipping}'] + [f'{taxable}'] + [f'{barcode}'] + [f'{get_href}'])

    
        # geting rid of empty lines in csv
        df = pd.read_csv(f'bin/{spreadsheet_name}', encoding = 'unicode_escape')
        output_name = spreadsheet_name + "_output.csv"
        df.to_csv(f'upload/{output_name}', index=False)

        print(colored(f"Saved as {output_name}", "green"))
        # with open(f"{main_dir}/{sub_dir}/{subsub_dir}/{subsub_dir}.txt", "w") as f:
        #     f.write("testing")
        #     f.close()
        # scrape into that directory that is created


    # def category(self):
        # html = self.driver.page_source # getting current page source
        # soup = BeautifulSoup(html, features="html.parser")

        # try:
        #     details = soup.find_all("a", attrs={"class":"grid-link"})
        #     srcs = soup.find_all("img", attrs={"class":"grid-image"})
        # except:
        #     print(colored("Something went wrong finding product information", "red"))
        #     print(colored("Are you on a category?", "blue"))
        
        # try:
        #     prices = soup.find_all("span", attrs={"class":"special-price"})
        # except:
        #     print(colored("Couldn't find prices of products", "red"))
        #     print(colored("Are you logged in?", "blue"))
        
        # try:
        #     title = soup.find('h1', {'class':'page-title'})
        #     print(title.text)
        #     category = title.text
        # except:
        #     print(colored("Couldn't find category name","red"))
        #     category = "Untitled"

        # href_list = []
        # title_list = []
        # price_list = []

        # #searching through classes
        # for i in details:
        #     get_href = i["href"]
        #     href_list.append(get_href)
        #     title_list.append(i.text)

        # for p in prices:
        #     p = p.text
        #     x = p.replace("Special Price", " ")
        #     y = x.replace("£"," ")
        #     price_list.append(y.strip())
        
        # if not price_list:
        #     print(colored("Couldn't get prices","red"))
        #     print(colored("Make sure you're on a category","blue"))
        #     quit()
        # else:
        #     None

        # # checking spreaadsheet name is okay
        # spreadsheetCount = 0
        # print(" ")
        # print(colored("Making spreadsheet..","green"))
        # spreadsheet_name = f"{category}"

        # special_characters = '"!@#$%^&*()-+?_=,<>/"'

        # if any(s in special_characters for s in category):
        #     re.sub('[^A-Za-z0-9]+', '', category)
        #     spreadsheet_name = f"{category}"
        # else:
        #     None

        # pwd = os.getcwd()
        # path = pwd + f"\\bin\\{spreadsheet_name}"
        # doessExist = os.path.exists(path)
        # if doessExist:
        #     print(colored(f"Spreadsheet {spreadsheet_name} already exists", "blue"))
        #     print(" ")
        #     while spreadsheetCount < 5:
        #         spreadsheet_name = f"{category}{spreadsheetCount}"
        #         if exists(spreadsheet_name):
        #             spreadsheetCount += 1
        #         else:
        #             print(colored(f"Creating {spreadsheet_name}", "green"))
        #             spreadsheetCount = 6
        # else:
        #     print(colored(f"Creating {spreadsheet_name}", "green"))

        # vendor = "TEG"
        # type = " "
        # tags = " "
        # option1 = "Title"
        # option1value = "Default Title"
        # variantgrams = "0"
        # inventory = "shopify"
        # qty = "999"
        # policy = "deny"
        # fulfill = "manual"
        # shipping = "TRUE"
        # taxable = "TRUE"
        # barcode = " "
        # published = "TRUE"
        # discount = None
        # manual = True
        # compareAtPrice = " "

        # with open(f'bin/{spreadsheet_name}', mode='w') as employee_file:

        #     employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #     employee_writer.writerow(['Handle'] + ['Title'] + ['Body (HTML)'] + ['Vendor'] + ['Type'] + ['Tags'] + ['Published'] + ['Option1 Name'] + ['Option1 Value'] + ['Variant Grams'] + ['Variant Inventory Tracker'] + ['Variant Inventory Qty'] + ['Variant Inventory Policy'] + ['Variant Fulfillment Service'] + ['Variant Price'] + ['Variant Compare At Price'] + ['Variant Requires Shipping'] + ['Variant Taxable'] + ['Variant Barcode'] + ['Image Src'])

        #     for title, url, price in zip(title_list, href_list, price_list):
        #         print(title)
        #         print(url)
        #         # print(price)
        #         price = float(price)
        #         price = format(price, '.2f')
        #         price = float(price)
        #         print("Old price:",price)
        #         percent = price/100*45 # 45% of price
        #         price = price + percent # adding percentage back to price
        #         price = float(price)
        #         price = format(price, '.2f')
        #         price = float(price)
        #         print("Updated price:",price)    

        #         handle = "-".join(title.split()).lower()

        #         a = requests.get(url)
        #         soup = BeautifulSoup(a.text, features="html.parser")
            
        #         d = soup.find('div', {'class':'product__accordion-content-inner'})
        #         desc = d.text # description
        #         print(desc)

        #         table = soup.find('table', {'class':'product__techspec'})
        #         print(table)
  
        #         final = str(desc) + "<br>" + "<br>" + str(table)
        #         all_images = []
        #         count = 0
        #         newcount = 1
        #         product_images = soup.find_all('a', {'class':'gallery__thumb-link'})
        #         for i in product_images:
        #             get_href = i["href"]
        #             all_images.append(get_href)
        #             print(get_href)
        #             count += 1
        #         # if it has more than one product image display it separately
        #         if count > 1:
        #             employee_writer.writerow([f'{handle}'] + [f'{title}'] + [f'{final}'] + [f'{vendor}'] + [f'{type}'] + [f'{tags}'] + [f'{published}'] + [f'{option1}'] + [f'{option1value}'] + [f'{variantgrams}'] + [f'{inventory}'] + [f'{qty}'] + [f'{policy}'] + [f'{fulfill}'] + [f'{price}'] + [f'{compareAtPrice}'] + [f'{shipping}'] + [f'{taxable}'] + [f'{barcode}'])
        #             for image in all_images:
        #                 employee_writer.writerow([f'{handle}'] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [' '] + [f'{image}'])
        #         else:
        #             employee_writer.writerow([f'{handle}'] + [f'{title}'] + [f'{final}'] + [f'{vendor}'] + [f'{type}'] + [f'{tags}'] + [f'{published}'] + [f'{option1}'] + [f'{option1value}'] + [f'{variantgrams}'] + [f'{inventory}'] + [f'{qty}'] + [f'{policy}'] + [f'{fulfill}'] + [f'{price}'] + [f'{compareAtPrice}'] + [f'{shipping}'] + [f'{taxable}'] + [f'{barcode}'] + [f'{get_href}'])

    
        # # geting rid of empty lines in csv
        # df = pd.read_csv(f'bin/{spreadsheet_name}', encoding = 'unicode_escape')
        # output_name = spreadsheet_name + "_output.csv"
        # df.to_csv(f'upload/{output_name}', index=False)

        # print(colored(f"Saved as {output_name}", "green"))
        
Scrape()

        # finalHref_list = []

        # for url in href_list:
        #     print(colored(f"Fetching main {url}","blue"))
        #     a=requests.get(url)
        #     s=bs4.BeautifulSoup(a.text,features="html.parser")
        #     title = s.find('h1', {'class':'page-title'}) # getting page title and making it a folder
        #     sub_dir = title.text.strip()
        #     os.mkdir(f"{main_dir}/{sub_dir}")
        #     print(colored("Sub directory '% s' built" % sub_dir, "green"))
        #     print("GETTING LINKS")
        #     cards = s.find_all("a", attrs={"class":"card__link"}) # getting links from page
        #     for card in cards:
        #         get_href = card["href"] 
        #         finalHref_list.append(get_href)
        #     print(finalHref_list)


        #     print(" ")
        #     print("GOING THROUGH LINK LIST")
        #     for i in finalHref_list:
        #         print(colored(f"Fetching {i}","green"))
        #         a=requests.get(i)
        #         s=bs4.BeautifulSoup(a.text,features="html.parser")
        #         t = s.find('h1', {'class':'page-title'}) # getting page title and making it a folder
        #         subsub_dir = t.text.strip()
        #         os.makedirs(f"{main_dir}/{sub_dir}/{subsub_dir}")    
        #         print(colored("Nested directory '% s' built" % subsub_dir, "green"))
        #         sleep(2)                
                        

        #     print(colored("Directory '% s' built" % sub_dir, "green"))
        #     print(colored("Sub directory '% s' built" % subsub_dir, "green"))
        #     sleep(2)



        # if signedIn:
        #     self.driver.get("https://www.gspen.co.uk/")
        #     None
        # else:
        #     print(colored("LOGGING IN","blue"))
        #     self.driver.get("https://www.gspen.co.uk/customer/account/login")
        #     sleep(1)
        #     self.driver.find_element(By.NAME, "login[username]").send_keys(user)
        #     sleep(1)
        #     self.driver.find_element(By.NAME, "login[password]").send_keys(pw)
        #     sleep(1)
        #     self.driver.find_element(By.NAME, "send").click()