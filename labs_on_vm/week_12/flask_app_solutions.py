import flask
import psycopg2
import redis
import json
import uuid
import hashlib


connection = psycopg2.connect(
    user = "postgres",
    password = "ucb",
    host = "postgres",
    port = "5432",
    database = "postgres"
)

cursor = connection.cursor()


session_db = redis.Redis(host='redis', port=6379, db=10)
session_db.flushdb()


def my_query_products():
    "query the products from Postgres and return a Python list of products"
    
    connection.rollback()

    query = """
    
    select p.product_id, p.description, sum(quantity), sum(quantity * 12)
    from products p
         join line_items l
             on p.product_id = l.product_id
    group by p.product_id, p.description
    order by p.product_id
    
    """
    
    cursor.execute(query)
    
    rows = cursor.fetchall()

    connection.rollback()
    
    products_list = []
    
    for row in rows:
        
        products_list.append([row[0], row[1], f'{row[2]:,}', f'{row[3]:,}'])
        
    return(products_list)

def my_query_stores():
    "query the stores from Postgres and return a Python list of stores"
    
    connection.rollback()

    query = """
    
    select s.store_id, s.city, sum(sa.total_amount)
    from stores as s
         join sales as sa
             on s.store_id = sa.store_id
    group by s.store_id, s.city
    order by s.store_id
    
    """
    
    cursor.execute(query)
    
    rows = cursor.fetchall()

    connection.rollback()
    
    stores_list = []
    
    for row in rows:
        
        stores_list.append([row[0], row[1], f'{row[2]:,}'])
        
    return(stores_list)


def validate_login(username, password):
    "given a username and password, return True if login is valid, False otherwise"
    
    password_sha256 = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    connection.rollback()
    
    query = """
    
        select *
        from web_api_users 
        where username = %s and password_sha256 = %s
    
    """
    
    cursor.execute(query, (username, password_sha256))
    
    return cursor.rowcount != 0


def my_create_sid():
    "create a SID based on mac address, a uuid number, concatenated, utf-8 encoded, and sha256 hashed"
    
    mac = uuid.getnode()
    
    universal_unique_id = uuid.uuid4()
    
    concatenated_string = str(mac) + str(universal_unique_id)
    
    sha256_string = hashlib.sha256(concatenated_string.encode('utf-8')).hexdigest()
    
    return sha256_string
    

app = flask.Flask(__name__)


@app.route("/api/login", methods=["POST"])
def api_login():
    
    username = flask.request.form['username']
    password = flask.request.form['password']
    
    if validate_login(username, password):
        
        sid = my_create_sid()
        
        session_db.set(sid, username)
        
        return_json = { "status": "success",
                        "sid": sid}
        
    else:
        
        return_json = { "status": "fail",
                        "description": "invalid username and/or password"}
    
    return(json.dumps(return_json))

 
@app.route("/api/logout", methods=["POST"])
def api_logout():
    
    sid = flask.request.form['sid']
    
    if session_db.get(sid) == None:
        
        return_json = { "status": "fail",
                        "description": "not logged in"}
    
    else: 
    
        session_db.delete(sid)

        return_json = { "status": "success" }
    
    return(json.dumps(return_json))


@app.route("/api/products", methods=["POST"])
def api_products():
    
    sid = flask.request.form['sid']
    
    if session_db.get(sid) == None:
        
        return_json = { "status": "fail",
                        "description": "not logged in"}
    
    else: 
        
        products_list = my_query_products()

        products_json_list = []

        for product in products_list:

            p = {}
            p["product_id"] = str(product[0])
            p["product_name"] = product[1]
            p["quantity"] = str(product[2])
            p["total_sales"] = str(product[3])

            products_json_list.append(p)
            
        return_json = { "status": "success",
                        "products": products_json_list}

    return(json.dumps(return_json))


@app.route("/api/stores", methods=["POST"])
def api_stores():
    
    sid = flask.request.form['sid']
    
    if session_db.get(sid) == None:
        
        return_json = { "status": "fail",
                        "description": "not logged in"}
    
    else: 
        
        stores_list = my_query_stores()
    
        stores_json_list = []
    
        for store in stores_list:
            
            s = {}
            s["store_id"] = str(store[0])
            s["city"] = store[1]
            s["total_sales"] = str(store[2])

            stores_json_list.append(s)
            
        return_json = { "status": "success",
                        "stores": stores_json_list}

    return(json.dumps(return_json))

