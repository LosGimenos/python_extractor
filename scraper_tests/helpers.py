import re
import datetime
import pytz
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import random

from .models import Review, Product

def calculate_review_stats(project, product):
    product.total_number_reviews = Review.objects.filter(project=project,
                                                         product=product).count()
    product.num_reviews_one_star = Review.objects.filter(project=project,
                                                         product=product,rating=float(1)).count()
    product.num_reviews_two_stars = Review.objects.filter(project=project,
                                                         product=product,rating=float(2)).count()
    product.num_reviews_three_stars = Review.objects.filter(project=project,
                                                         product=product,rating=float(3)).count()
    product.num_reviews_four_stars = Review.objects.filter(project=project,
                                                         product=product,rating=float(4)).count()
    product.num_reviews_five_stars = Review.objects.filter(project=project,
                                                         product=product,rating=float(5)).count()
    product.save()

def click_element(driver,xpath):

    succeeded = False
    num_attempts = 0
    max_num_attempts = 5
    while succeeded == False:
        num_attempts += 1
        if num_attempts > max_num_attempts:
            break
        try:
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            element.click()
            succeeded = True
            print("Succeeded clicking link")
            return "Success"
        except:
            print("Error clicking link")
            time.sleep(random.randint(3,4))
    return "Error"

def click_element_by_hitting_enter(driver,xpath):

    succeeded = False
    num_attempts = 0
    max_num_attempts = 10
    while succeeded == False:
        num_attempts += 1
        if num_attempts > max_num_attempts:
            break
        try:
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            element.send_keys(Keys.RETURN)
            succeeded = True
            print("Succeeded clicking link by hitting enter")
            return "Success"
        except:
            print("Error clicking link by hitting enter")
            time.sleep(random.randint(3,4))
    return "Error"


def click_elements(driver,xpath):

    succeeded = False
    num_attempts = 0
    max_num_attempts = 10
    while succeeded == False:
        num_attempts += 1
        if num_attempts > max_num_attempts:
            break
        try:
            elements = WebDriverWait(driver, 4).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
            for element in elements:
                element.click()
            succeeded = True
            print("Succeeded clicking link")
        except:
            print("Error clicking link")
            time.sleep(random.randint(1,2))

def get_element(driver,xpath,error_message):

    succeeded = False
    num_attempts = 0
    max_num_attempts = 10
    while succeeded == False:
        num_attempts += 1
        if num_attempts > max_num_attempts:
            break
        try:
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element.text
        except:
            print(error_message)
            # time.sleep(random.randint(3,4))
            return "Error"

def get_elements(driver,xpath,error_message):

    succeeded = False
    num_attempts = 0
    max_num_attempts = 10
    while succeeded == False:
        num_attempts += 1
        if num_attempts > max_num_attempts:
            break
        try:
            elements = WebDriverWait(driver, 8).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
            print("Got elements")
            return elements
        except:
            print(error_message)
            time.sleep(random.randint(3,4))
            return "Error"

def convert_date_to_datetime(day_regex, month_regex, year_regex, date_to_convert):
    if date_to_convert.find('hour') > 0:
        date_to_convert = '1 day'
    day_matches = re.findall(day_regex, date_to_convert)
    if len(day_matches) == 0:
        month_matches = re.findall(month_regex, date_to_convert)
        if len(month_matches) == 0:
            year_matches = re.findall(year_regex, date_to_convert)
            year_delta = year_matches[0]
            day_delta = int(year_delta) * 365
            converted_date = datetime.datetime.today() - datetime.timedelta(days=day_delta)
            review_date = converted_date.replace(tzinfo=pytz.UTC)
        else:
            month_delta = month_matches[0]
            day_delta = int(month_delta) * 30
            converted_date = datetime.datetime.today() - datetime.timedelta(days=day_delta)
            review_date = converted_date.replace(tzinfo=pytz.UTC)
    else:
        day_delta = int(day_matches[0])
        converted_date = datetime.datetime.today() - datetime.timedelta(days=day_delta)
        review_date = converted_date.replace(tzinfo=pytz.UTC)
    return review_date

def check_date_against_cutoff_date(review, cutoff_date, start_date):
    if review.date < cutoff_date or review.date > start_date:
        print('deleted review', review)
        review.delete()

def convert_date_a_to_one(regex_date, date_text):
    date_regex_matches = re.findall(regex_date, date_text)

    if len(date_regex_matches) == 0:
        regex_date = 'a year ago'
        date_regex_matches = re.findall(regex_date, date_text)
        if len(date_regex_matches) == 0:
            regex_date = 'a month ago'
            date_regex_matches = re.findall(regex_date, date_text)
            if len(date_regex_matches) == 0:
                regex_date = 'a day ago'
                date_regex_matches = re.findall(regex_date, date_text)
                if len(date_regex_matches) == 0:
                    logger.warn("No matches - find last date")
                else:
                    individual_review_date = "1 day ago"
            else:
                individual_review_date = "1 month ago"
        else:
            individual_review_date = "1 year ago"
    else:
        individual_review_date = date_regex_matches[0]
    return individual_review_date
