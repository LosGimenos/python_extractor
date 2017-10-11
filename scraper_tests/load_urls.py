from openpyxl import Workbook, load_workbook
import re
import requests
from .models import Project, Product, Review, ProductPageUrl
import datetime
import pytz
import logging
import codecs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
import random
import os

def load_review_url_file():

    path = 'scraper_tests/review_urls/reviews_oct.xlsx'
    project_name = 'Neutrogena Beauty'


    # 1 instance of block
    if Project.objects.filter(project_id=project_name).exists():
        project = Project.objects.get(project_id=project_name)
    else:
        project = Project(project_id = project_name)
        project.save()


    wb = load_workbook(path, read_only=True)

    for ws in wb:

        for index, row in enumerate(ws.rows):

            if index == 0:
                continue

            ppu = ProductPageUrl(project=project,source=row[0].value,brand=row[2].value,
                                 group=row[3].value,product_line=row[4].value,product=row[5].value,
                                 url=row[6].value,source_data_path='')
            # if order_list[0] != 'NA':
            #     ppu.source = row[order_list[0]-1].value
            # if order_list[1] != 'NA':
            #     ppu.brand = row[order_list[1]-1].value
            ppu.save()
