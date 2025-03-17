from pushbullet import Pushbullet
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Replace this with your Pushbullet API Key
API_KEY = os.getenv("PUSHBULLET_API_KEY")

# Initialize Pushbullet
pb = Pushbullet(API_KEY)

# Read the products from products.json
with open('products.json', 'r') as file:
    products = json.load(file)

# Loop through products and check if the discount is 70% or more
for product in products:
    
    discount_percentage = (product['original_price'] - product['discounted_price']) / product['original_price'] * 100
    
    if discount_percentage >= 70:
        print(f"{product['product_name']} is now {discount_percentage:.2f}% off! Check it out: {product['product_link']}")
        # Send a notification if the discount is greater than or equal to 70%
        message = f"{product['product_name']} is now {discount_percentage:.2f}% off! Check it out: {product['product_link']}"
        pb.push_note(f"Great Deal on {product['product_name']}", message)

print("Notifications sent successfully!")
