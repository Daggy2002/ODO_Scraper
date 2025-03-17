from playwright.sync_api import sync_playwright
import json
import time

BASE_URL = "https://www.onedayonly.co.za"

def scrape_products():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL, wait_until='networkidle')

        # Get scrollable height
        body_scroll_height = page.evaluate("document.body.scrollHeight")
        window_inner_height = page.evaluate("window.innerHeight")
        num_of_scrolls = body_scroll_height // window_inner_height

        products = []

        def extract_products():
            """Extracts product details from the current page view."""
            product_divs = page.query_selector_all('div.measure-this.css-xkwvql, div.measure-this.css-1vky73n')
            for product_div in product_divs:
                # Get brand & product name
                name_div = product_div.query_selector('div.css-tejrt9')
                if not name_div:
                    continue
                
                h2_tags = name_div.query_selector_all('h2')
                if len(h2_tags) < 2:
                    continue  # Ensure both brand and product name exist
                
                brand = h2_tags[0].inner_text().strip()
                product_name = h2_tags[1].inner_text().strip()

                # Get price details
                price_div = product_div.query_selector('div.css-s7w4za')
                discounted_price = original_price = None

                if price_div:
                    h2_prices = price_div.query_selector_all('h2')
                    def convert_price(price_str):
                        """Convert price string 'R#,##' to integer."""
                        return int(price_str.replace('R', '').replace(',', '').strip())

                    if len(h2_prices) == 3:
                        discounted_price = convert_price(h2_prices[1].inner_text().strip())
                        original_price = convert_price(h2_prices[2].inner_text().strip())
                    elif len(h2_prices) == 2:
                        discounted_price = convert_price(h2_prices[0].inner_text().strip())
                        original_price = convert_price(h2_prices[1].inner_text().strip())

                # Extract product link
                link_tag = product_div.query_selector('a')
                relative_link = link_tag.get_attribute("href") if link_tag else None
                full_link = BASE_URL + relative_link if relative_link else None

                products.append({
                    "brand": brand,
                    "product_name": product_name,
                    "discounted_price": discounted_price,
                    "original_price": original_price,
                    "product_link": full_link
                })

        # **Extract before scrolling to ensure first products are captured**
        extract_products()

        # Scroll and extract additional products
        for i in range(num_of_scrolls):
            page.evaluate(f"window.scrollTo(0, {window_inner_height * (i + 1)})")
            time.sleep(1)  # Allow time for content to load
            extract_products()  # Extract products after scrolling

        browser.close()
        
        # Remove duplicate entries
        unique_products = {json.dumps(product, sort_keys=True): product for product in products}.values()
        products = list(unique_products)

        # Save to JSON
        with open('products.json', 'w', encoding='utf-8') as file:
            json.dump(products, file, indent=4, ensure_ascii=False)

scrape_products()
