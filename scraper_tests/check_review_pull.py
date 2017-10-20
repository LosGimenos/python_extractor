import datetime
import pytz
import os
from selenium import webdriver
import logging
from .amazon import get_amazon_reviews
# from .walmart import get_walmart_reviews
from .walmart_soup import get_walmart_reviews
from .target import get_target_reviews_js
# from .walgreens import get_walgreens_reviews_js
from .walgreens_fix import get_walgreens_reviews_js
from .ulta import get_ulta_reviews_js
from .makeupalley import get_makeup_alley_reviews_js
from .target_from_api import get_target_reviews_api
from .models import ProductPageUrl, Product, Review, Project
from .redis_testing_queue import get_redis_queue, set_redis_queue
from openpyxl import Workbook, load_workbook
from .helpers import *

logger = logging.getLogger(__name__)

# reviews = Review.objects.filter(product=2424)

# for review in reviews:
#     print(review.id)

def local_calculate_review_stats(project, product_id):
    product = Product.objects.get(id=product_id)

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

local_calculate_review_stats(project=1, product_id=2433)
