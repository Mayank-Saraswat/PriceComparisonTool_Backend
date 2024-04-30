from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

app = Flask(__name__)

def get_amazon_price(product):
    url = f'https://www.amazon.in/s?k={product.replace(" ", "+")}'
    headers = {
        'User-Agent': 'Your User Agent Here',
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    price_tag = soup.find('span', {'class': 'a-price-whole'})
    if price_tag:
        return price_tag.text.replace(',', '')
    else:
        return "Price not found on Amazon"

# def get_croma_price(product):
#     url = f'https://www.croma.com/search/?text={product.replace(" ", "%20")}'
#     headers = {
#         'User-Agent': 'Your User Agent Here',
#     }
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     price_tag = soup.find('span', {'class': 'amount'})
#     if price_tag:
#         return price_tag.text.replace(',', '')
#     else:
#         return "Price not found on Croma"

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

@app.route('/api/prices', methods=['GET'])
def get_prices():
    product = request.args.get('product')
    if not product:
        return jsonify({"error": "Please provide a product name"}), 400
    amazon_price = get_amazon_price(product)
    # croma_price = get_croma_price(product)
    flipkart_price = get_flipkart_price(product)

    prices = {
        'Amazon': amazon_price,
        # 'Croma': croma_price,
        'Flipkart': flipkart_price
    }

    response = jsonify(prices)
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow all origins
    return response

if __name__ == '__main__':
    app.run(debug=True)
