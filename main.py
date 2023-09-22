from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


#   Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/random')
def get_random_cafe():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)

    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def get_all():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    cafes_list = [cafe.to_dict() for cafe in all_cafes]

    return jsonify(cafes=cafes_list)


@app.route('/search')
def search_cafe():
    location = request.args.get('loc')
    result = db.session.execute(db.select(Cafe).order_by(Cafe.location))
    all_cafes = result.scalars().all()

    cafes_list = [cafe.to_dict() for cafe in all_cafes if cafe.location.lower() == location.lower()]

    if cafes_list:
        return jsonify(cafes=cafes_list)
    else:
        return jsonify(error={
            "Not found": "Sorry, we don't have a cafe at that location."
        })


@app.route("/add", methods=['POST'])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get('name'),
        map_url=request.form.get('map_url'),
        img_url=request.form.get('img_url'),
        location=request.form.get('location'),
        seats=request.form.get('seats'),
        has_toilet=bool(request.form.get('has_toilet')),
        has_wifi=bool(request.form.get('has_wifi')),
        has_sockets=bool(request.form.get('has_sockets')),
        can_take_calls=bool(request.form.get('can_take_calls')),
        coffee_price=request.form.get('coffee_price'),
    )
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={
        "success": "Successfully added the new cafe."
    })


@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get('new_price')
    coffee_to_update = db.session.get(Cafe, cafe_id)

    if coffee_to_update:
        coffee_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify({
            "success": "Successfully updated the price."
        }), 200
    else:
        return jsonify(error={
            "Not Found": "Sorry a cafe with that id was not found in the database"
        }), 404


@app.route("/report-closed/<int:cafe_id>", methods=['DELETE'])
def delete_cafe(cafe_id):
    api_key = "TopSecretAPIKey"
    user_api_key = request.args.get('api_key')
    cafe_to_delete = db.session.get(Cafe, cafe_id)

    if cafe_to_delete:
        if api_key == user_api_key:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify({
                "success": "Successfully deleted."
            }), 200
        else:
            return jsonify(error={
                "error": "Sorry that's not allowed. Make sure you have the correct api_key"
            }), 401
    else:
        return jsonify(error={
            "error": "Sorry a cafe with that id was not found in the database"
        }), 404


if __name__ == '__main__':
    app.run(debug=True)
