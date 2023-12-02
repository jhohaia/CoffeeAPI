from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)

def extract_brand_name(coffeeUrl):
    
    parsed_url = urlparse(coffeeUrl)
    
    # Extract the brand name from the domain
    domain = parsed_url.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    brand = domain.split('.')[0]

    if "coffee" in brand.lower():
        # Add a space before and after "coffee"
        brand = brand.replace("coffee", " coffee ")

    brand = brand.strip().capitalize()

    return brand

def scrape_data(coffeeUrl, description_page_types, title_page_types):
    brand = extract_brand_name(coffeeUrl)
    response = requests.get(coffeeUrl)
    soup = BeautifulSoup(response.content, "html.parser")
    
    titles = []
    
    for title_type in title_page_types:
        if title_type == "h1_title":
            for title in soup.find_all("h1"):
                titles.append(title.text)
            break
        elif title_type == "h2_title":
            for title in soup.find_all("h2"):
                titles.append(title.text)
            break
    
    descriptions = []

    for page_type in description_page_types:
        if page_type == "p_tag":
            description_container = soup.find(class_="product-block--description__text")
            if description_container:
                for p_tag in description_container.find_all("p"):
                    descriptions.append(p_tag.text)
                break  
        elif page_type == "div_tag":
            description_container = soup.find(class_="product-description rte")
            if description_container:
                for div in description_container.find_all("div"):
                    # Add additional conditions to filter specific div elements if needed
                    descriptions.append(div.get_text(separator=" ", strip=True))
                break 

    prices = []
    for price in soup.find_all("span", class_=["RetailPrice", "money", "appstle_subscription_amount transcy-money"]):
        prices.append(price.text)
    
    return brand, titles, descriptions, prices

@app.route("/<path:coffeeUrl>")
def home(coffeeUrl):
    # Define a list of page types to try in order
    title_page_types = ["h1_title", "h2_title"]
    description_page_types = ["p_tag", "div_tag"]

    brand, titles, descriptions, prices = scrape_data(coffeeUrl, description_page_types, title_page_types)
    return render_template("index.html", brand=brand, titles=titles, descriptions=descriptions, prices=prices)

if __name__ == "__main__":
    app.run(debug=True)
