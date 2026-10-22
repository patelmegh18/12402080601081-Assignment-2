import sys
import re

PRODUCT_PATTERN = re.compile(
    r'class=["\']name["\']>([^<]+)<.*?class=["\']price["\'>]*[^0-9]*([0-9]+(?:\.[0-9]+)?).*?class=["\']rating["\'>]*([0-9]+(?:\.[0-9]+)?)',
    re.DOTALL | re.IGNORECASE
)

def extract_products(file_paths):
    catalog = {}
    for path in file_paths:
        try:
            with open(path.strip(), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = PRODUCT_PATTERN.findall(content)
                for name, price, rating in matches:
                    p_name = name.strip()
                    p_price = float(price)
                    p_rating = float(rating)
                    if p_name not in catalog:
                        catalog[p_name] = (p_price, p_rating)
                    else:
                        if p_rating > catalog[p_name][1]:
                            catalog[p_name] = (p_price, p_rating)
        except FileNotFoundError:
            continue
    return catalog

def rank_products(catalog, k):
    items = [(name, price, rating) for name, (price, rating) in catalog.items()]
    items.sort(key=lambda x: (-x[2], x[1], x[0]))
    for name, price, rating in items[:k]:
        display_price = int(price) if price.is_integer() else price
        print(f"{name} {display_price} {rating}")

if __name__ == '__main__':
    data = sys.stdin.read().splitlines()
    if not data:
        sys.exit(0)
    p, k = map(int, data[0].split())
    paths = data[1:p + 1]
    products = extract_products(paths)
    rank_products(products, k)
