import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'pc_store.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500))
    is_custom = db.Column(db.Boolean, default=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product', backref='cart_items')

def get_cart_html():
    """Возвращает HTML корзины"""
    cart_items = CartItem.query.all()
    total_sum = sum(item.product.price * item.quantity for item in cart_items)
    
    if not cart_items:
        return '<div class="empty-cart"><span>🛒</span><p>Корзина пуста</p></div>'
    
    html = '<div class="cart-items">'
    for item in cart_items:
        html += f'''
        <div class="cart-item">
            <div class="cart-item-info">
                <div class="cart-item-name">{item.product.name}</div>
                <div class="cart-item-price">{item.product.price:.0f} ₽ × {item.quantity}</div>
            </div>
            <form method="POST" action="{url_for('remove_from_cart', item_id=item.id)}" onclick="removeItem(event, {item.id})">
                <button type="submit" class="btn-remove">✕</button>
            </form>
        </div>
        '''
    html += '</div>'
    html += f'''
    <div class="cart-total">
        <p>Итого</p>
        <p class="sum">{total_sum:.0f} ₽</p>
    </div>
    <form method="POST" action="{url_for('clear_cart')}" onsubmit="clearCart(event)">
        <button type="submit" class="btn btn-clear">Очистить</button>
    </form>
    '''
    return html

# def init_products():
#     """Initialize default products"""
#     if Product.query.count() == 0:
#         products = [
#             Product(name="RTX 4090", category="Видеокарта", price=150000, description="Мощная видеокарта для игр"),
#             Product(name="Ryzen 9 7900X", category="Процессор", price=45000, description="12-ядерный процессор"),
#             Product(name="DDR5 32GB", category="Оперативная память", price=12000, description="32GB DDR5 памяти"),
#             Product(name="SSD 2TB NVMe", category="Накопитель", price=15000, description="Быстрый SSD накопитель"),
#             Product(name="Материнская плата", category="Материнская плата", price=35000, description="AM5 сокет"),
#             Product(name="Блок питания 1000W", category="БП", price=18000, description="80+ Gold сертификация"),
#         ]
#         for product in products:
#             db.session.add(product)
#         db.session.commit()

@app.route('/')
def index():
    products = Product.query.filter_by(is_custom=False).all()
    cart_items = CartItem.query.all()
    total_sum = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('index.html', products=products, cart_items=cart_items, total_sum=total_sum)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        return redirect(url_for('index'))
    
    cart_item = CartItem.query.filter_by(product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(product_id=product_id, quantity=1)
        db.session.add(cart_item)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_items = CartItem.query.all()
        total_sum = sum(item.product.price * item.quantity for item in cart_items)
        return jsonify({'success': True, 'total_sum': total_sum, 'cart_html': get_cart_html()})
    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    cart_item = CartItem.query.get(item_id)
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_items = CartItem.query.all()
        total_sum = sum(item.product.price * item.quantity for item in cart_items)
        return jsonify({'success': True, 'total_sum': total_sum, 'cart_html': get_cart_html()})
    return redirect(url_for('index'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    CartItem.query.delete()
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'total_sum': 0, 'cart_html': get_cart_html()})
    return redirect(url_for('index'))

@app.route('/add_custom_product', methods=['POST'])
def add_custom_product():
    data = request.get_json()
    name = data.get('name', '').strip()
    price = data.get('price', 0)
    
    if not name or price <= 0:
        return jsonify({'success': False, 'error': 'Введите корректные данные'}), 400
    
    try:
        price = float(price)
        product = Product(name=name, category='Пользовательский', price=price, description='', is_custom=True)
        db.session.add(product)
        db.session.commit()
        
        cart_item = CartItem(product_id=product.id, quantity=1)
        db.session.add(cart_item)
        db.session.commit()
        
        cart_items = CartItem.query.all()
        total_sum = sum(item.product.price * item.quantity for item in cart_items)
        
        return jsonify({
            'success': True,
            'product_id': product.id,
            'product_name': product.name,
            'product_price': product.price,
            'cart_html': get_cart_html()
        })
    except ValueError:
        return jsonify({'success': False, 'error': 'Цена должна быть числом'}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # init_products()
    app.run(debug=True)
