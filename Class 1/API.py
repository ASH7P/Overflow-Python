from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hobby = db.Column(db.String(100))
    email = db.Column(db.String(100))

class Credintials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(20))

# Initialize the database and create tables
with app.app_context():
    db.create_all()


# GET all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "name": user.name, "hobby": user.hobby, "email": user.email} for user in users])

# GET a specific user by ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({"id": user.id, "name": user.name, "hobby": user.hobby, "email": user.email})

# POST a new user
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    
    new_user = User(name=data['name'], hobby=data.get('hobby'), email=data.get('email'))
    db.session.add(new_user)
    db.session.commit()
    
    # Reload the user from the database to get it bound to the session again
    reloaded_user = User.query.get(new_user.id)
    
    return jsonify({
        "message": "User created",
        "user": {
            "id": reloaded_user.id,
            "name": reloaded_user.name,
            "hobby": reloaded_user.hobby,
            "email": reloaded_user.email
        }
    }), 201

# PUT to update an existing user by ID
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get_or_404(id)
    
    user.name = data.get('name', user.name)
    user.hobby = data.get('hobby', user.hobby)
    user.email = data.get('email', user.email)
    
    db.session.commit()
    return jsonify({"message": "User updated", "user": {"id": user.id, "name": user.name, "hobby": user.hobby, "email": user.email}})

# DELETE a user by ID
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 204

@app.route('/basic-auth/<int:id>/<string:password>')
def basic_auth(id, password):
    # Query the database for a matching user
    credentials = Credintials.query.filter_by(id=id, password=password).first()
    
    if credentials:
        # If the user is found, return their data
        return jsonify({
            'id': credentials.id,
            'location' : credentials.location
        }), 200
    else:
        # If no match is found, return a 404 error
        abort(404, description="User not found or password incorrect.")


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
