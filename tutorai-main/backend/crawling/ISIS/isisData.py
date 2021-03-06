import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.firefox.options import Options

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

from tkinter import *
from tkinter.ttk import *
from functools import partial

import json

import csv

import concurrent.futures

from time import sleep

class ISISWebdriver():
    def __init__(self, url, user_agend):
        self.url = url
        self.ua = user_agend
        self.userName = None
        self.pw = None
        self.isLoggedIn = False
        self.data = {}
        self.foren = None
        self.driver = self.getDriver()

    def getDriver(self):

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'----user-agent={self.ua}')
        #chrome_options.add_argument('--headless')

        driver = webdriver.Chrome(executable_path="C:\SeleniumDrivers\chromedriver.exe", options=chrome_options)
        return driver

    def setLogin(self):
        self.userName = self.entry_name.get()
        self.pw = self.entry_pw.get()
        self.master.destroy()

    def setLoginData(self):
        self.master = Tk()
        self.master.geometry("900x400")
        label_front = Label(self.master, text="Geben Sie bitte ihre Isis login Daten ein")
        label_front.config(font=("Courier", 25))
        label_front.pack(pady=30)

        label_name = Label(self.master, text="Username")
        label_name.pack()

        self.entry_name = Entry(self.master)
        self.entry_name.pack()

        label_pw = Label(self.master, text="Password")
        label_pw.pack()

        self.entry_pw = Entry(self.master)
        self.entry_pw.pack()

        button_save = Button(self.master, text="submit", command = self.setLogin)
        button_save.pack()
        mainloop()

    def login(self):
        self.setLoginData()

        try:

            self.driver.get(self.url)
            time.sleep(2)
            tu_login_btn = self.driver.find_element_by_id("shibbolethbutton")
            tu_login_btn.submit()
            time.sleep(2)

            username = self.driver.find_element_by_name("j_username")
            username.send_keys(self.userName)
            time.sleep(2)
            pwd = self.driver.find_element_by_name("j_password")
            pwd.send_keys(self.pw)
            time.sleep(2)

            submit_login = self.driver.find_element_by_id("login-button")
            submit_login.click()

            time.sleep(3)
            if self.driver.current_url == "https://isis.tu-berlin.de/my/":
                self.userName = None
                self.pw = None
                self.isLoggedIn = True

        except:
            self.setLoginData()


    def search_course(self, course):
        search_box = self.driver.find_element_by_id("navsearchbox")
        time.sleep(2)
        search_box.send_keys(course)
        search_box.submit()
        time.sleep(4)

        search_result = self.driver.find_element_by_class_name("aalink")
        search_result.click()

        self.course = {"name":course,"link":self.driver.current_url,"messages":[]}
        #self.courseName = course
        time.sleep(3)




    def getData(self):
        time.sleep(2)
        #title = self.driver.find_element_by_class_name("discussionname")
        #title = title.text
        #content = self.driver.find_elements_by_class_name("post-content-container")
        #links = self.driver.find_elements_by_class_name("btn.btn-link")
        #links = self.driver.find_elements_by_link_text("Dauerlink")
        #print(test[0].get_attribute("href"))
        #print(links[0].get_property('attributes')[0])
        container = self.driver.find_elements_by_class_name("d-flex.body-content-container")

        messages = []
        counter = 0

        for content in container:
            text_elem = content.find_element_by_class_name("post-content-container")
            text = text_elem.text
            text = text.replace("\n"," ")

            link_elem = content.find_element_by_link_text("Dauerlink")
            link = link_elem.get_attribute("href")
            if text != "+1":
                messages.append({"text":text,"answers_in_thread":len(container),"tutor_answer_in_thread":"","link": link})
                counter += 1
        #data = {'title': title, 'posts': messages}
        self.driver.back()
        return messages


    def clickLink(self):
        time.sleep(3)
        #forum = self.course[self.courseName]["forum"]
        counter = 0
        for f in self.foren:
            #link = self.driver.find_element_by_link_text(f["name"])
            """if "IntroProg" in f["name"]:
                self.driver.get(f["link"])
                time.sleep(3)
            else:
                pass"""

            self.driver.get(f["link"])
            time.sleep(3)

            liste = self.driver.find_elements_by_class_name("w-100.h-100.d-block")

            #self.course[self.courseName]["forum"][counter]["entry"] = []
            #page_link = self.driver.find_element_by_link_text("Next")

            while True:
                liste = self.driver.find_elements_by_class_name("w-100.h-100.d-block")
                for i in range(len(liste)):
                    time.sleep(3)
                    liste = self.driver.find_elements_by_class_name("w-100.h-100.d-block")
                    print(i,len(liste))
                    liste[i].click()
                    #self.course[self.courseName]["forum"][counter]["entry"].append(self.getData())
                    self.course["messages"].extend(self.getData())
                    time.sleep(2)
                try:
                    next_link = self.driver.find_element_by_css_selector("[aria-label=Next]")
                    next_link.click()
                except:
                    break


            self.driver.back()
            counter += 1

    def getForenFromCourse(self,key):
        allActivities = self.driver.find_elements_by_class_name("aalink")
        self.foren = []

        #self.course[key]["forum"] = []

        for activities in allActivities:
            ac_link = activities.get_attribute('href')

            if "forum" in ac_link:
                ac_name = activities.find_element_by_class_name("instancename").text
                #self.course[key]["forum"].append({"name":ac_name,"link":ac_link})
                self.foren.append({"name":ac_name,"link":ac_link})



if __name__ == "__main__":
    url = "https://www.isis.tu-berlin.de"
    user_agend = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
    #course = "IntroProg"
    #foren = ["Nachrichtenforum","C-Kurs","Offenes Forum","IntroProg"]

    course = ["WS 20/21 ODS Einf??hrung in die Programmierung","WS 19/20 ODS Einf??hrung in die Programmierung"]
    course_name = ["2021_Einfuehrung_Programmierung", "1920_Einfuehrung_Programmierung"]

    #foren = ["C-Kurs", "Offenes Forum", "H??ufig gestellte Fragen und technische Fragen zu Hausaufgaben und Vorlesungen im Semester","Nachrichtenforum"]
    crowler = ISISWebdriver(url, user_agend)

    while crowler.isLoggedIn == False:
        crowler.login()

    c = 0
    for course in course:
        crowler.course = None
        crowler.search_course(course)
        crowler.getForenFromCourse(course)
        crowler.clickLink()
        crowl_data = crowler.course

        with open(f'{course_name[c]}.json', 'w') as outfile:
            json.dump(crowl_data, outfile)
        c += 1

    print("JSON Created ................")




