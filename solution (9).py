import sys

class Product:
    def __init__(self, pid, name, stock, purchase_price, selling_price):
        self.pid = pid
        self.name = name
        self.stock = int(stock)
        self.purchase_price = float(purchase_price)
        self.selling_price = float(selling_price)

    def __repr__(self):
        p_price = int(self.purchase_price) if self.purchase_price.is_integer() else self.purchase_price
        s_price = int(self.selling_price) if self.selling_price.is_integer() else self.selling_price
        return f"{self.pid} {self.name} stock={self.stock} purchase={p_price} selling={s_price}"

class Inventory:
    def __init__(self):
        self.products = {}

    def add_product(self, product):
        if product.pid in self.products:
            cur = self.products[product.pid]
            cur.stock += product.stock
            cur.purchase_price = min(cur.purchase_price, product.purchase_price)
            cur.selling_price = max(cur.selling_price, product.selling_price)
        else:
            self.products[product.pid] = product

    def delete_product(self, pid):
        return self.products.pop(pid, None)

    def update_stock(self, pid, qty):
        if pid in self.products:
            self.products[pid].stock = int(qty)
            return True
        return False

    def total_valuation(self):
        return sum(p.stock * p.selling_price for p in self.products.values())

    def __add__(self, other):
        merged = Inventory()
        for p in self.products.values():
            merged.add_product(Product(p.pid, p.name, p.stock, p.purchase_price, p.selling_price))
        for p in other.products.values():
            merged.add_product(Product(p.pid, p.name, p.stock, p.purchase_price, p.selling_price))
        return merged

    def __lt__(self, other):
        return self.total_valuation() < other.total_valuation()

    def __eq__(self, other):
        return self.total_valuation() == other.total_valuation()

def load_from_file(path):
    inv = Inventory()
    try:
        with open(path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    inv.add_product(Product(parts[0], parts[1], parts[2], parts[3], parts[4]))
    except FileNotFoundError:
        pass
    return inv

if __name__ == '__main__':
    inv_a = load_from_file('inv_a.txt')
    inv_b = load_from_file('inv_b.txt')

    merged_inv = inv_a + inv_b
    for item in merged_inv.products.values():
        print(item)
