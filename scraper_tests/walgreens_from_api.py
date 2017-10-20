import re
import requests
from .models import Project, Product, Review, ProductPageUrl
import html
import datetime
import pytz
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import random
import os
import json

from .helpers import *

logger = logging.getLogger(__name__)

def get_walgreens_reviews_js(headers_list, product_page_url, project, product, start_date, cutoff_date, brand_website_name):

    # url = 'https://api.bazaarvoice.com/data/batch.json?passkey=tpcm2y0z48bicyt0z3et5n2xf&apiversion=5.5&displaycode=2001-en_us&resource.q0=reviews&filter.q0=isratingsonly%3Aeq%3Afalse&filter.q0=productid%3Aeq%3Aprod6339648&filter.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort.q0=submissiontime%3Adesc&stats.q0=reviews&filteredstats.q0=reviews&include.q0=authors%2Cproducts%2Ccomments&filter_reviews.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_comments.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&limit.q0=100&offset.q0=0&limit_comments.q0=1&callback=bv_1111_58120'
    # page_source = requests.get(url, headers=random.choice(headers_list)).json()
    urls = [ 'https://api.bazaarvoice.com/data/batch.json?passkey=tpcm2y0z48bicyt0z3et5n2xf&apiversion=5.5&displaycode=2001-en_us&resource.q0=products&filter.q0=id%3Aeq%3Aprod6359561&stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews&filter_questions.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_answers.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviews.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&resource.q1=questions&filter.q1=productid%3Aeq%3Aprod6359561&filter.q1=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort.q1=lastapprovedanswersubmissiontime%3Adesc&stats.q1=questions&filteredstats.q1=questions&include.q1=authors%2Cproducts%2Canswers&filter_questions.q1=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_answers.q1=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort_answers.q1=submissiontime%3Adesc&limit.q1=10&offset.q1=0&limit_answers.q1=10&resource.q2=reviews&filter.q2=isratingsonly%3Aeq%3Afalse&filter.q2=productid%3Aeq%3Aprod6359561&filter.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort.q2=relevancy%3Aa1&stats.q2=reviews&filteredstats.q2=reviews&include.q2=authors%2Cproducts%2Ccomments&filter_reviews.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviewcomments.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_comments.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&limit.q2=100&offset.q2=0&limit_comments.q2=1&callback=bv_1111_58120',
        'https://api.bazaarvoice.com/data/batch.json?passkey=tpcm2y0z48bicyt0z3et5n2xf&apiversion=5.5&displaycode=2001-en_us&resource.q0=products&filter.q0=id%3Aeq%3Aprod6359561&stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews&filter_questions.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_answers.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviews.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&resource.q1=questions&filter.q1=productid%3Aeq%3Aprod6359561&filter.q1=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort.q1=lastapprovedanswersubmissiontime%3Adesc&stats.q1=questions&filteredstats.q1=questions&include.q1=authors%2Cproducts%2Canswers&filter_questions.q1=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_answers.q1=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort_answers.q1=submissiontime%3Adesc&limit.q1=10&offset.q1=0&limit_answers.q1=10&resource.q2=reviews&filter.q2=isratingsonly%3Aeq%3Afalse&filter.q2=productid%3Aeq%3Aprod6359561&filter.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort.q2=relevancy%3Aa1&stats.q2=reviews&filteredstats.q2=reviews&include.q2=authors%2Cproducts%2Ccomments&filter_reviews.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviewcomments.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_comments.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&limit.q2=100&offset.q2=100&limit_comments.q2=1&callback=bv_1111_58120',
        'https://api.bazaarvoice.com/data/batch.json?passkey=tpcm2y0z48bicyt0z3et5n2xf&apiversion=5.5&displaycode=2001-en_us&resource.q0=products&filter.q0=id%3Aeq%3Aprod6359561&stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews&filter_questions.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_answers.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviews.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&resource.q1=questions&filter.q1=productid%3Aeq%3Aprod6359561&filter.q1=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort.q1=lastapprovedanswersubmissiontime%3Adesc&stats.q1=questions&filteredstats.q1=questions&include.q1=authors%2Cproducts%2Canswers&filter_questions.q1=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_answers.q1=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort_answers.q1=submissiontime%3Adesc&limit.q1=10&offset.q1=0&limit_answers.q1=10&resource.q2=reviews&filter.q2=isratingsonly%3Aeq%3Afalse&filter.q2=productid%3Aeq%3Aprod6359561&filter.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort.q2=relevancy%3Aa1&stats.q2=reviews&filteredstats.q2=reviews&include.q2=authors%2Cproducts%2Ccomments&filter_reviews.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviewcomments.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_comments.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&limit.q2=100&offset.q2=200&limit_comments.q2=1&callback=bv_1111_58120',
        'https://api.bazaarvoice.com/data/batch.json?passkey=tpcm2y0z48bicyt0z3et5n2xf&apiversion=5.5&displaycode=2001-en_us&resource.q0=products&filter.q0=id%3Aeq%3Aprod6359561&stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews&filter_questions.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_answers.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviews.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&resource.q1=questions&filter.q1=productid%3Aeq%3Aprod6359561&filter.q1=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort.q1=lastapprovedanswersubmissiontime%3Adesc&stats.q1=questions&filteredstats.q1=questions&include.q1=authors%2Cproducts%2Canswers&filter_questions.q1=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_answers.q1=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort_answers.q1=submissiontime%3Adesc&limit.q1=10&offset.q1=0&limit_answers.q1=10&resource.q2=reviews&filter.q2=isratingsonly%3Aeq%3Afalse&filter.q2=productid%3Aeq%3Aprod6359561&filter.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&sort.q2=relevancy%3Aa1&stats.q2=reviews&filteredstats.q2=reviews&include.q2=authors%2Cproducts%2Ccomments&filter_reviews.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_reviewcomments.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&filter_comments.q2=contentlocale%3Aeq%3Aen%2Cen_AU%2Cen_CA%2Cen_GB%2Cen_US&limit.q2=100&offset.q2=300&limit_comments.q2=1&callback=bv_1111_58120']

    for url in urls:
        page_source = requests.get(url, headers=random.choice(headers_list)).text
        page_source = page_source[:-1]
        page_source = page_source[14:]
        try:
            page_source = json.loads(page_source)
        except:
            print(page_source[:100])

        try:
            product.total_number_reviews = page_source['BatchedResults']['q2']['TotalResults']
            product.save()
            reviews = page_source['BatchedResults']['q2']['Results']
        except:
            logger.warn(page_source)

        for item in reviews:
            review_date = item['SubmissionTime']
            review_date = review_date.split("T")[0]
            review_date = datetime.datetime.strptime(review_date, "%Y-%m-%d").replace(tzinfo=pytz.UTC)

            if review_date > start_date:
                continue

            if review_date < cutoff_date:
                return

            review_text = item['ReviewText']
            title = item['Title']

            if item['IsSyndicated']:
                is_from_brand_website = item['SyndicationSource']['Name']
            else:
                is_from_brand_website = ''

            if item['IsRecommended']:
                would_recommend = 'would recommend'
            else:
                would_recommend = 'would not recommend'

            rating = item['Rating']
            username = item['UserNickname']

            review = Review(project=project, product=product, date=review_date, title=title,
                            username=username, review_text=review_text,
                            rating=float(rating), is_from_brand_website=is_from_brand_website,
                            would_recommend=would_recommend)

            review.save()
            calculate_review_stats(project, product)
