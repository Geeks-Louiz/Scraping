import requests
import ast
import logging
import argparse
from pandas import DataFrame
from bs4 import BeautifulSoup
from datetime import datetime


logging.basicConfig(level=logging.INFO)

PAGE_OFFSET_INTERVAL = 30
BASE_URL = "https://www.tripadvisor.com"

DATE = datetime.now().strftime("%Y-%m-%d")


def get_html_and_parse(url):
    req = requests.get(url)
    url_html = BeautifulSoup(req.text, "html.parser")
    return url_html


def _get_last_page_offset(url_html): # pour oubtenir la derniere page 
    
    page_numbers = url_html.findAll("div", attrs={"class": "pageNumbers"})[0]
    last_page_offset = page_numbers.findAll("a")[-1].get("data-offset")
    return int(last_page_offset)


def _restaurant_info(restaurant_data):
    restaurant_dict = {
        "name": restaurant_data.get("name"),
        "address": restaurant_data.get("address").get("streetAddress"),
        "tel":restaurant_data.get("tel").get("phonenumber"),
        "email":restaurant_data.get("email").get("emails"),
        "priceRange": restaurant_data.get("priceRange"),
        "rating": restaurant_data.get("aggregateRating").get("ratingValue"),
        "reviewCount": restaurant_data.get("aggregateRating").get("reviewCount"),
        "address": restaurant_data.get("address").get("streetAddress"),
        "locality": restaurant_data.get("address").get("addressLocality"),

        "url": BASE_URL + restaurant_data.get("url"),
    }
    return restaurant_dict


def city_filter(city):
    city_filter = {
        "Panama C": ("g187147", "Paris_Ile_de_France"),
        "Lyon": ("g187265","Lyon_Rhone_Auvergne_Rhone_Alpes"),
        "Nantes": ("g187198","Nantes_Loire_Atlantique_Pays_de_la_Loire"),
        "La_def": ("g1934807","La_Defense_Hauts_de_Seine_Ile_de_France"),
        "Saint_Maurice": ("g562740","Bourg_Saint_Maurice_Savoie_Auvergne_Rhone_Alpes"),
        "Versailles": ("g29458", "Versailles_Yvelines_Ile_de_France"),
        "NANTERRE": ("g236589", "Nanterre_La_Defense_Hauts_de_Seine_Ile_de_France"),
        "Montreil": ("g294080", "Montreuil_Hauts_de_Seine_Ile_de_France"),
        "SAINT CLOUD": ("g86659", "Saint_cloud_Hauts_de_Seine_Ile_de_France"),
        
    }
    city_information = city_filter.get(city)
    if city_information is None:
        logging.error(f"Available cities: {list(city_filter.keys())}")
    else:
        return city_information


def get_restaurants_info(restaurants_list, url_html):
    # trouver et sauveharder les infos restau dans une liste 
    #list va contenir tte les infos du restau url_html retourner avec beautiful_soup va contenir html de la page scraper
    
    def get_restaurant_info(restaurant_tag):
        restaurant_url = BASE_URL + restaurant_tag.get("href")
        restaurant_html = get_html_and_parse(restaurant_url)
        restaurant_data = restaurant_html.findAll("script")[1].contents[0]
        restaurant_data = ast.literal_eval(restaurant_data)
        restaurant_information = _restaurant_info(restaurant_data)
        if restaurant_information:
            restaurants_list.append(restaurant_information)
        

    restaurants_component = url_html.findAll(attrs={"id": "component_2"})
    restaurants_tags = filter(
        lambda x: x.get("href").startswith("/Restaurant_Review")
                  and x.get("href").endswith("#REVIEWS"),
        restaurants_component[0].findAll("a"),
    )


def _set_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", type=str, required=True, help="Need to specify a city")
    parser.add_argument("--max_pages", type=int)
    args, unknown = parser.parse_known_args()
    return args


def _make_csv(restaurants_lists, city, date):
    columns = list(restaurants_lists[0].keys())
    df = DataFrame(restaurants_lists, columns=columns)
    csv_name = f"Restaurants_{city}_{date}.csv"
    logging.info(f"Saving CSV as {csv_name}")
    df.to_csv(csv_name, index=False)


if __name__ == "__main__":
    args = _set_cli()
    restaurants_data = []
    city_code, city_name = city_filter(args.city)
    logging.info(f"Scraping Tripadvisor restaurants data from {args.city}")

    page_offset = 0
    full_url = BASE_URL + f"/Restaurants-{city_code}-oa{page_offset}-{city_name}"
    first_page = get_html_and_parse(full_url)
    if not args.max_pages:
        last_page_offset = _get_last_page_offset(first_page)
    else:
        last_page_offset = (args.max_pages - 1) * PAGE_OFFSET_INTERVAL
    last_page = (last_page_offset / PAGE_OFFSET_INTERVAL) + 1

    logging.info(f"Scraping page 1 of {int(last_page)}")
    
    first_page_info = get_restaurants_info(restaurants_data, first_page)
    while page_offset < last_page_offset:
        page_offset += PAGE_OFFSET_INTERVAL
        page_number = (page_offset / PAGE_OFFSET_INTERVAL) + 1
        page_html = get_html_and_parse(full_url)
        logging.info(f"Scraping page {int(page_number)} of {int(last_page)}")
        restaurants_information = get_restaurants_info(
            restaurants_data, page_html
        )
    _make_csv(restaurants_data, args.city, DATE)

