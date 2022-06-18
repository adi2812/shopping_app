from flask import Blueprint, render_template, request, flash,redirect, url_for,jsonify
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required,login_user
from .models import User, Category, Product, Cart, Orders
from . import db, UPLOAD_FOLDER
import os
import json
from sqlalchemy import delete
import uuid


views = Blueprint('views',__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

@views.route("/")
@login_required
def index():
    categories = Category.query.all()
    return render_template("index.html",user=current_user,categories=categories)

@views.route("/admin_login", methods=['GET',"POST"])
def admin_login():
    if request.method == "POST":
        userid = request.form['userid']
        password = request.form['password']

        user = User.query.filter_by(first_name=userid).first()

        if user:
            if user.first_name == "admin":
                if check_password_hash(user.password,password):
                    flash("Logged in successfully",category='success')
                    login_user(user,remember=True)
                    return redirect(url_for('views.admin'))
                else:
                    flash("Wrong password",category="error")
            else:
                flash("Not a admin",category="error")
        else:
            flash("User doesn't exist",category="error")
        

    return render_template("admin/admin_login.html", user= current_user)


@views.route("/admin")
@login_required
def admin():
    if current_user.first_name == 'admin':
        products = Product.query.all()
        categories = Category.query.all()
        return render_template("admin/admin.html",user=current_user,products=products,categories=categories)
    else:
        flash("Only Admin can access the area", category="error")
        return redirect(url_for("views.index"))

@views.route('/admin/add_category',methods=["GET","POST"])
@login_required
def add_category():
    if current_user.first_name == 'admin':
        if request.method == 'POST':
            category_name = request.form['category']
            cate = Category.query.filter_by(name=category_name).first()
            if not cate:
                if category_name.isalpha():
                    if "image" in request.files:
                        file = request.files['image']
                        if file.filename == '':
                            category = Category(name=category_name)
                            #flash('No selected file',category='error')
                            #return redirect(url_for('views.add_category'))
                        else:
                            if file and allowed_file(file.filename):
                                #filename = secure_filename(file.filename)
                                _, file_extension = os.path.splitext(file.filename)
                                filename = uuid.uuid4().hex + file_extension
                                file.save(os.path.join(UPLOAD_FOLDER, filename))
                                category = Category(name=category_name,image=filename)
                            else:
                                flash('Wrong selected file',category='error')
                                return redirect(url_for('views.add_category'))
                    #else:
                    #    category = Category(name=category_name)
                    db.session.add(category)
                    db.session.commit()
                    flash("Category created", category = 'success')
                    return redirect(url_for('views.add_category'))
                else:
                    flash("Please write a Alphabetical name",category="error")
                    return redirect(url_for('views.add_category'))
            else:
                flash("Category already present",category="error")
                return redirect(url_for('views.add_category'))
        else:
            if current_user.first_name == 'admin':
                category = Category.query.all()
                return render_template("admin/add_category.html",user=current_user,categories=category)
            else:
                flash("Only Admin can access the area", category="error")
                return redirect(url_for("views.index"))
    else:
        flash("Only Admin can access the area", category="error")
        return redirect(url_for("views.index"))

@views.route('/admin/add_product',methods=["GET","POST"])
@login_required
def add_product():
    if current_user.first_name == 'admin':
        if request.method == 'POST':
            product_name = request.form['name']
            price = request.form['price']
            brand = request.form['brand']
            quantity = request.form['quantity']
            #size = request.form['size']
            category = request.form['category']
            description = request.form['description']
            filename = ""
            product = Product.query.filter_by(name=product_name).first()
            if not product:
                #Image Upload
                if "image" in request.files:
                    file = request.files['image']
                    if file.filename == '':
                        product = Product(name=product_name,price=price,brand=brand,qty=quantity,category_id=category,description=description)
                    else:
                        if file and allowed_file(file.filename):
                            #filename = secure_filename(file.filename)
                            _, file_extension = os.path.splitext(file.filename)
                            filename = uuid.uuid4().hex + file_extension
                            file.save(os.path.join(UPLOAD_FOLDER, filename))
                            product = Product(name=product_name,price=price,brand=brand,qty=quantity,category_id=category,description=description, image=filename)
                        else:
                            flash('Wrong selected file',category='error')
                            return redirect(url_for('views.add_product'))
                db.session.add(product)
                db.session.commit()
                flash("Product created", category = 'success')
                return redirect(url_for('views.admin'))
            else:
                flash("Product already present",category="error")
                return redirect(url_for('views.add_category'))

        else:
            if current_user.first_name == 'admin':
                categories = Category.query.all()
                return render_template("admin/add_product.html",user=current_user, categories = categories)
            else:
                flash("Only Admin can access the page", category="error")
                return redirect(url_for("views.index"))
    else:
        flash("Only Admin can access the page", category="error")
        return redirect(url_for("views.index"))

@views.route("/delete_product",methods=["POST"])
def delete_note():
    data_product = json.loads(request.data)
    productID = data_product["productID"]
    note = Product.query.get(productID)

    if note:
        if note.image != "image.jpg":
            filename = os.path.join(UPLOAD_FOLDER, note.image)
            if os.path.exists(filename):
                os.remove(filename)
        db.session.delete(note)
        db.session.commit()

    return jsonify({})


@views.route("/admin/edit_product/<int:id>",methods=['GET','POST'])
@login_required
def edit_product(id):
    if current_user.first_name == 'admin':
        if request.method == "POST":    
            product_name = request.form['name']
            price = request.form['price']
            brand = request.form['brand']
            quantity = request.form['quantity']
            category = request.form['category']
            description = request.form['description']
            file = request.files['image']

            print(category)
            product = Product.query.get(id)

            if file.filename != "":
                if file and allowed_file(file.filename):
                    if product.image != "image.jpg":
                        filename = os.path.join(UPLOAD_FOLDER, product.image)
                        if os.path.exists(filename):
                            os.remove(filename)
                    _, file_extension = os.path.splitext(file.filename)
                    filename = uuid.uuid4().hex + file_extension
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    product.image = filename
                else:
                    flash("Wrong file type",category='error')

            product.name = product_name
            product.price = price
            product.qty = quantity
            product.brand = brand
            product.category_id = category
            product.description = description
            
            db.session.commit()
            flash("Product updated",category="success")
            return redirect(url_for("views.admin"))
        else:
            product = Product.query.get(id)
            if current_user.first_name == 'admin':
                categories = Category.query.all()
            return render_template('/admin/edit_product.html',product=product,user=current_user,categories=categories)
    else:
        flash("Only Admin can access the page", category="error")
        return redirect(url_for("views.index"))

@views.route("/delete_category",methods=["GET","POST"])
def delete_category():
    if request.method == "POST":
        data_category = json.loads(request.data)
        productID = data_category["categoryID"]
        note = Category.query.get(productID)
        if note:
            if note.image != "image.jpg":
                filename = os.path.join(UPLOAD_FOLDER, note.image)
                if os.path.exists(filename):
                    os.remove(filename)
            db.session.delete(note)
            db.session.commit()
        return jsonify({})


@views.route('/<category>/products')
@login_required
def products(category):
    categories = Category.query.all()
    category_obj = Category.query.filter_by(name = category).first()
    if category_obj:
        products = db.session.query(Product).filter(category_obj.id == Product.category_id, Product.qty > 1).all()
        if products:
            return render_template("products.html",products=products, user=current_user, categories=categories)
        else:
            flash("No products availabe in the category please try later")
            return redirect(url_for('views.index'))
    else:
        flash("The category you are looking might not be present",category="error")
        return redirect(url_for('views.index'))

@views.route("/<product>/product_details")
@login_required
def product_detail(product):
    categories = Category.query.all()
    product_details = Product.query.filter_by(name=product).first()
    if product_details:
        return render_template("product_detail.html",user = current_user,product = product_details,categories=categories)
    else:
        flash("The product you are looking might not be present",category="error")
        return redirect(url_for('views.index'))


@views.route("/addtocart", methods=['GET','POST'])
@login_required
def addtocart():
    if request.method == "POST":
        productID = request.form["product_id"]
        quantity = request.form['quantity']
        #print(data)
        #print(current_user.id)
        #Check if product in stock
        #Add a product in cart using product id 
        product = Product.query.get(productID)
        if product.qty > 0:
            cart = Cart(product_id=productID,quantity=quantity,user_id=current_user.id)
            #product.qty -= product.qty - quantity
            db.session.add(cart)
            db.session.add(product)
            db.session.commit()
            flash("Product added to cart",category='success')
            return redirect(url_for('views.display_cart'))
        else:
            flash("Product is out of stock sorry", category='error')
            return redirect(url_for('views.index'))
        ###During checkout check the number of products left
    else:
        return redirect(url_for('views.index'))

@views.route("/cart")
@login_required
def display_cart():
    #cart_products = Cart.query.get()
    cart_products = Cart.query.filter_by(user_id=current_user.id).all()
    products = Product.query.all()
    categories = Category.query.all()
    data = []
    
    total = 0
    for pro in cart_products:
        product_dict = {}
        for product in products:
            product_dict['quantity'] = pro.quantity
            product_dict['cart_id'] = pro.id
            if pro.product_id == product.id:
                product_dict['product_name'] = product.name
                product_dict['product_brand'] = product.brand
                product_dict['product_price'] = product.price
                #product_dict['id'] = cart_products.id
                for category in categories:
                    if product.category_id == category.id:
                        product_dict['category_name'] = category.name
                data.append(product_dict)
                total += (product.price*pro.quantity)
    return render_template("cart.html", user=current_user, data=data, total=total,categories=categories)

@views.route("/remove_from_cart",methods=["POST"])
@login_required
def remove_from_cart():
    if request.method == "POST":
        data_category = json.loads(request.data)
        productID = data_category["categoryID"]
        note = Cart.query.get(productID)
        if note:
            db.session.delete(note)
            db.session.commit()
        return jsonify({})

@views.route("/edit_cart/<int:id>",methods=["GET","POST"])
def edit_cart(id):
    category = Category.query.all() 
    cart = Cart.query.get(id)
    if request.method == "POST":
        data = request.form['quantity']
        cart.quantity = data
        db.session.commit()
        flash("Quantity updated")
        return redirect(url_for('views.display_cart'))
    else:
        if cart:
            product = Product.query.filter_by(id=cart.product_id)
            return render_template('edit_cart.html',cart=cart,user=current_user,product=product,categories=category)
        else:
            flash("Invalid request")
            return redirect("views.index")


@views.route("/checkout",methods=['GET','POST'])
@login_required
def checkout():
    if request.method == "POST":
        data = request.form['flexRadioDefault']

        bought_products = Cart.query.filter_by(user_id=current_user.id).all()

        for product in bought_products:
            product_id = product.product_id
            quantity = product.quantity
            user_id = current_user.id
            order = Orders(product_id=product_id,quantity=quantity,user_id=user_id)
            product_main = Product.query.get(product_id)
            print(product_id)
            product_main.qty -= quantity
            db.session.add(order)

        d = Cart.query.filter_by(user_id = current_user.id).all()
        for i in d:
            db.session.delete(i)
        db.session.commit()
        return redirect(url_for("views.my_orders")) 
    else:
        bought_products = Cart.query.filter_by(user_id=current_user.id).all()
        products = Product.query.all()
        categories = Category.query.all()

        data = []
        total = 0

        for product in bought_products:
            product_dict = {}
            product_dict['quantity'] = product.quantity
            product_dict['product_price'] = Product.query.get(product.product_id).price
            product_dict['cart_id'] = Product.query.get(product.product_id).id
            product_dict['product_name'] = Product.query.get(product.product_id).name
            product_dict['product_brand'] = Product.query.get(product.product_id).brand
            product_dict['category_name'] = Category.query.get(Product.query.get(product.product_id).category_id).name 
            data.append(product_dict)
            total += (Product.query.get(product.product_id).price * product.quantity)
        return render_template("checkout.html", user=current_user, data=data, total=total,categories=categories)


@views.route('/my_orders')
@login_required
def my_orders():
    categories = Category.query.all()
    my_orders = Orders.query.filter_by(user_id=current_user.id).all()
    #products = Product.query.filter_by(product_id__in=[ord.product_id for ord in my_orders])
    order_data = []
    for order in my_orders:
        data = {}
        data["product_name"] = Product.query.get(order.product_id).name
        data["brand"] = Product.query.get(order.product_id).brand
        data["price"] = Product.query.get(order.product_id).price
        data["category_name"] = Category.query.get(Product.query.get(order.product_id).category_id).name 
        data["ordered_on"] = order.ordered_on
        data["quantity"] = order.quantity
        data["accepted"] = order.order_accepted
        data["dispatched"] = order.order_dispatched
        data["delivered"] = order.order_delivered
        data["order_id"] = order.id
        order_data.append(data)
    
    return render_template('my_orders.html',my_orders=order_data,user=current_user,categories=categories)


@views.route("/all_orders")
@login_required
def all_orders():
    if current_user.first_name == 'admin':
        if request.method == "POST":
            return "Good Job"
        else:
            all_orders = Orders.query.all()
            order_data = []
            for order in all_orders:
                data = {}
                data["id"] = order.id
                data["product_name"] = Product.query.get(order.product_id).name
                data["brand"] = Product.query.get(order.product_id).brand
                data["price"] = Product.query.get(order.product_id).price
                data["category_name"] = Category.query.get(Product.query.get(order.product_id).category_id).name 
                data["ordered_on"] = order.ordered_on
                data["quantity"] = order.quantity
                data["accepted"] = order.order_accepted
                data["dispatched"] = order.order_dispatched
                data["delivered"] = order.order_delivered
                data["order_id"] = order.id
                data["user_id"] = User.query.get(order.user_id).id
                data["user_name"] = User.query.get(order.user_id).first_name
                data["user_address"] = User.query.get(order.user_id).address
                order_data.append(data)
            return render_template("admin/all_orders.html",orders=order_data,user=current_user)
    
    else:
        flash("Only Admin can access the page", category="error")
        return redirect(url_for("views.index"))


@views.route("/update_order/<int:id>",methods=["POST"])
@login_required
def update_order(id):
    if current_user.first_name == "admin":
        if request.method == "POST":
            # accepted = request.form["accepted"]
            # dispatched = request.form["dispatched"]
            # delivered = request.form["delivered"]
            order = Orders.query.get(id)
            data = request.form
            if "accepted" in data:
                order.order_accepted = True
            else:
                order.order_accepted = False

            if "dispatched" in data:
                order.order_dispatched= True
            else:
                order.order_dispatched= False
            
            if "delivered" in data:
                order.order_delivered = True
            else:
                order.order_delivered = False

            db.session.commit()
                
            return redirect(url_for("views.all_orders"))
        else:
            return redirect(url_for("views.all_orders"))
    else:
        flash("Only Admin can access the page", category="error")
        return redirect(url_for("views.index"))
