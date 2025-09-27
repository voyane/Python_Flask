from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user




app = Flask(__name__)
app.config['SECRET_KEY'] = "minha_chave_1234"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = "login"
CORS(app)


#Modelagem
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False, unique = True)
    password = db.Column(db.String(20), nullable = True)
    cart = db.relationship('CartItem', backref = 'user', lazy = True)

#Autenticação
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods = ["POST"])
def login():
    data = request.get_json()

    #recuperar o usuario direti da base de dados
    user = User.query.filter_by(username = data.get("username")).first()

    if user and data.get("password") == user.password:
            login_user(user)
            return jsonify({'message': "Logged in successfully!"})
    
    return jsonify({'message': "Unauthorized. Invalid credentials!"}), 401

@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({'message': "Logged out successfully!"})

#Produto (id, name, price, description)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), nullable = False)
    price = db.Column(db.Float, nullable = False)
    description = db.Column(db.Text, nullable = True)

#Adicionar produto
@app.route('/api/products/add', methods = ["POST"])
@login_required
def add_product():
    data = request.get_json()
    if not data:
        return jsonify({'message': "No input data provided!"}), 400
    
    if 'name' in data and 'price' in data:
        product = Product(
            name = data["name"], 
            price = data["price"], 
            description = data.get("description", "")
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': "Product added successfully!"})
    return jsonify({'message': "Invalid product data!"}), 400

#Eliminar produto
@app.route('/api/products/delete/<int:product_id>', methods = ["DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': "Product deleted successfully!"})
    return jsonify({'message': "Product not found!"}), 404

#Buscar produtos por ID
@app.route('/api/products/<int:product_id>', methods = ["GET"])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description                  
        })
    return jsonify({'message': "Product not found!"}), 404

#Listar Produto
@app.route('/api/products', methods = ["GET"])
def get_product():
    products = Product.query.all()
    return jsonify([
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "description": p.description
            }
            for p in products
    ])

#Atualizar produto
@app.route('/api/products/update/<int:product_id>', methods = ["PUT"])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': "Product not found!"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'message': "No input data provided!"}), 400
    
    if 'name' in data:
        product.name = data['name']

    if 'price' in data:
        try:
            product.price = float(data['price'])
        except ValueError:
            return jsonify({'message': "Price must be a number"}), 400

    if 'description' in data:
        product.description = data['description']

    db.session.commit()
    return jsonify({'message': "Product update successfully!"})

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable = False)

@app.route('/api/cart/add/<int:product_id>', methods = ["POST"])
@login_required
def add_to_cart(product_id):
    user = User.query.get(int(current_user.id))

    product = Product.query.get(product_id)

    if user and product:
        cart_item = CartItem(user_id = user.id, product_id = product.id)
        db.session.add(cart_item)
        db.session.commit()
        return jsonify({'message': "Item added to the cart successfully!"})
    return jsonify({'message': "Failed to add item to the cart!"}), 400

@app.route('/api/cart/remove/<int:product_id>', methods = ["DELETE"])
@login_required
def remove_cart(product_id):
    cart_item = CartItem.query.filter_by(user_id = current_user.id, product_id = product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': "Item removed from the cart successfully!"})
    return jsonify({'message': "Failed to remove item from the cart!"}), 400

@app.route('/api/cart', methods = ["GET"])
@login_required
def view_cart():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    cart_content = []
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        cart_content.append(
            {
                "id": cart_item.id,
                "product_id": cart_item.product_id,
                "product_name": product.name,
                "product_price": product.price
            }
        )
        return jsonify(cart_content)
    
@app.route('/api/cart/checkout', methods = ["POST"])
@login_required
def checkout_cart():
    user = User.query.get(int(current_user.id))
    cart_items = user.cart
    for cart_item in cart_items:
        db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': "Checkout successful. Cart has been cleared!"})

#Definir uma rota raiz(pagina inicial) e a função que será excutada ao requisitar 
@app.route('/')
def ecommerce_flask():
    return "E-commerce API 1.0.0 OAS 2.0"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)