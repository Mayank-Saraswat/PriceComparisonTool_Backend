from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import fake_useragent
from bs4 import BeautifulSoup
import mysql.connector

app = Flask(__name__)
CORS(app)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        port="3306",
        user='root',
        password='2001',
        database='pricecomparisondb'
    )

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

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM login_credentials WHERE Email = %s AND Pass = %s', (email, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for duplicate email
    cursor.execute('SELECT * FROM login_credentials WHERE Email = %s', (email,))
    user = cursor.fetchone()
    if user:
        cursor.close()
        conn.close()
        return jsonify({"error": "Email already exists"}), 409  # 409 Conflict

    cursor.execute('INSERT INTO login_credentials (Email, Pass) VALUES (%s, %s)', (email, password))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Signup successful"}), 201

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
