from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///apps.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class App(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(80), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=False)

# Ensure database tables are created
with app.app_context():
    db.create_all()

    # Import data from sample_data.sql (only if it's needed or not already populated)
    conn = sqlite3.connect('apps.db')
    cursor = conn.cursor()
    try:
        # Execute the sample_data.sql script to insert data
        with open('sample_data.sql', 'r') as f:
            cursor.executescript(f.read())
        conn.commit()
    except Exception as e:
        print(f"Error importing data: {e}")
    finally:
        conn.close()

@app.route('/add-app', methods=['POST'])
def add_app():
    data = request.json
    if not data or not all(key in data for key in ['app_name', 'version', 'description']):
        return jsonify({"error": "Invalid request body"}), 400

    new_app = App(
        app_name=data['app_name'],
        version=data['version'],
        description=data['description']
    )
    db.session.add(new_app)
    db.session.commit()

    return jsonify({"message": "App added successfully", "id": new_app.id}), 201

@app.route('/get-app/<int:id>', methods=['GET'])
def get_app(id):
    app = db.session.get(App, id)  # Updated to use session.get() instead of query.get()
    if not app:
        return {"error": "App not found"}, 404
    return {
        "id": app.id,
        "app_name": app.app_name,
        "version": app.version,
        "description": app.description
    }, 200

@app.route('/delete-app/<int:id>', methods=['DELETE'])
def delete_app(id):
    app_instance = db.session.get(App, id)  # Updated to use session.get() instead of query.get()
    if not app_instance:
        return jsonify({"error": "App not found"}), 404

    db.session.delete(app_instance)
    db.session.commit()

    return jsonify({"message": "App deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)
