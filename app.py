from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import fake_useragent
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

def extract_flipkart_image(product):
    try:
        search_url = f'https://www.flipkart.com/search?q={product.replace(" ", "%20")}'

        # Set user agent headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.amazon.in/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
        }

        # Send GET request to Amazon search URL
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract image URL of the first product
        img_wrapper = soup.find('div', {'class': '_4WELSP'})
        if img_wrapper:
            image_url = img_wrapper.find('img')['src']
            return image_url
        else:
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def get_amazon_price(product):
    url = f'https://www.amazon.in/s?k={product.replace(" ", "+")}'
    headers = {
        'User-Agent': fake_useragent.UserAgent().random,
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    price_tag = soup.find('span', {'class': 'a-price-whole'})
    if price_tag:
        return price_tag.text.replace(',', '')
    else:
        return "Price not found on Amazon"

def get_flipkart_price(product):
    url = f'https://www.flipkart.com/search?q={product.replace(" ", "%20")}'
    headers = {
        'User-Agent': 'Your User Agent Here',
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    price_tag = soup.find('div', {'class': 'Nx9bqj'})
    if price_tag:
        return price_tag.text.replace(',', '')
    else:
        return "Price not found on Flipkart"

@app.route('/', methods=['POST', 'GET'])
def start():
    return "Tool server is Running"

@app.route('/prices', methods=['GET'])
def get_prices():
    product = request.args.get('product')
    if not product:
        return jsonify({"error": "Please provide a product name"}), 400
    amazon_price = get_amazon_price(product)
    flipkart_price = get_flipkart_price(product)

    flipkart_image_url = extract_flipkart_image(product)

    prices = {
        'Amazon': amazon_price,
        'Flipkart': flipkart_price,
        'Flipkart_Image_URL': flipkart_image_url
    }
    response = jsonify(prices)
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow all origins
    return response
