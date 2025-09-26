from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

db = SQLAlchemy(app)

#Modelagem
#Produto (id, name, price, description)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), nullable = False)
    price = db.Column(db.Float, nullable = False)
    description = db.Column(db.Text, nullable = True)

#Adicionar produto
@app.route('/api/products/add', methods = ["POST"])
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
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': "Product deleted successfully!"})
    return jsonify({'message': "Product not found!"}), 404

#Buscar produtos por ID
@app.route('/api/products/<int:product_id>', methods = ["GET"])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description                  
        })
    return jsonify({'message': "Product not found!"}), 404

#Atualizar produto
@app.route('/api/products/update/<int:product_id>', methods = ["PUT"])
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

#Definir uma rota raiz(pagina inicial) e a função que será excutada ao requisitar 
@app.route('/')
def ecommerce_flask():
    return "E-commerce API 1.0.0 OAS 2.0"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)