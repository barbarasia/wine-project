import os
from flask import Flask, abort, request, jsonify, send_from_directory
import pymysql
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Swagger UI setup
swaggerui_blueprint = get_swaggerui_blueprint(
    '/docs',  # Swagger UI base URL
    '/static/openapi.yaml',  # OpenAPI specification file
)
app.register_blueprint(swaggerui_blueprint, url_prefix='/docs')

# Endpoint to serve the OpenAPI spec file
@app.route('/static/openapi.yaml')
def send_openapi_spec():
    return send_from_directory(os.path.dirname(__file__), 'openapi.yaml')

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password=os.getenv('sql_key'),
        database="wine_schema",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/wine_consumption', methods=['GET'])
def get_wine_consumption():
    country = request.args.get('country')
    year = request.args.get('year')
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT w.*, ct.Country
        FROM consowine AS w
        JOIN country AS ct ON w.country_id = ct.country_id
        WHERE w.Variable = 'Consumption'
    """
    params = []

    if country:
        query += " AND ct.Country = %s"
        params.append(country)
    if year:
        query += " AND w.Year = %s"
        params.append(year)

    print(f"Executing query: {query}")
    print(f"With parameters: {params}")

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    print(f"Query returned: {results}")

    if not results:
        return jsonify({"message": "No data found for the specified parameters"}), 404

    return jsonify(results)

@app.route('/wine_production', methods=['GET'])
def get_wine_production():
    country = request.args.get('country')
    year = request.args.get('year')
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT w.*, ct.Country
        FROM consowine AS w
        JOIN country AS ct ON w.country_id = ct.country_id
        WHERE w.Variable = 'Production'
    """
    params = []

    if country:
        query += " AND ct.Country = %s"
        params.append(country)
    if year:
        query += " AND w.Year = %s"
        params.append(year)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return jsonify(results)

@app.route('/alcohol_spending', methods=['GET'])
def get_alcohol_spending():
    year = request.args.get('year')
    alcohol_type = request.args.get('type')
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM alcohol_spending"
    params = []

    if year:
        query += " WHERE year = %s"
        params.append(year)
    if alcohol_type:
        if params:
            query += " AND type = %s"
        else:
            query += " WHERE type = %s"
        params.append(alcohol_type)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return jsonify(results)

@app.route('/top_producers', methods=['GET'])
def get_top_producers():
    wine_type = request.args.get('type')
    limit = request.args.get('limit', 10, type=int)
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT d.Dept_Name AS Region, r.Type, SUM(r.Production_Volume) AS Total_Production
        FROM regions_prod_loc AS r
        JOIN departement AS d ON r.departement_id = d.departement_id
        WHERE r.Type = %s
        GROUP BY d.Dept_Name, r.Type
        ORDER BY Total_Production DESC
        LIMIT %s
    """

    cursor.execute(query, (wine_type, limit))
    results = cursor.fetchall()
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)