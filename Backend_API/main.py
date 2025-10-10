# -----------------------------------------------------------------------------
# main.py - API Principal para la Aplicación Bancaria NowApp
# -----------------------------------------------------------------------------

# --- IMPORTACIONES ---
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
from bson import ObjectId

# --- CARGA DE VARIABLES DE ENTORNO ---
load_dotenv()

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE SEGURIDAD Y DE LA APLICACIÓN
# -----------------------------------------------------------------------------
SECRET_KEY = "un_secreto_muy_dificil_de_adivinar_y_muy_largo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(
    title="NowApp API",
    description="La API para gestionar las operaciones de la aplicación bancaria NowApp.",
    version="1.3.0"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE CORS
# -----------------------------------------------------------------------------
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# MODELOS DE DATOS (PYDANTIC)
# -----------------------------------------------------------------------------
class TransferRequest(BaseModel):
    cuenta_origen: str
    cuenta_destino: str
    monto: float

class ReviewRequest(BaseModel):
    score: int
    comment: str | None = None 

class AddToCartRequest(BaseModel):
    product_id: str
    quantity: int

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LA BASE DE DATOS
# -----------------------------------------------------------------------------
#PostgreSQL
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "BD_Transaccional_NowApp"
DB_USER = "admin"
DB_PASSWORD = "una_contraseña_muy_fuerte_123"

#MongoDB
MONGO_URI = os.getenv("MONGO_URI") # Lee la cadena de conexión del archivo .env
client = MongoClient(MONGO_URI) # Crea el cliente de MongoDB
db_mongo = client.nowapp_store  # Selecciona nuestra base de datos 'nowapp_store'

# -----------------------------------------------------------------------------
# FUNCIONES DE UTILIDAD
# -----------------------------------------------------------------------------
def get_db_connection():
    try:
        conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' port='{DB_PORT}' password='{DB_PASSWORD}'"
        conn = psycopg2.connect(conn_string)
        return conn
    except psycopg2.OperationalError as e:
        print(f"ERROR: No se pudo conectar a la base de datos: {e}")
        return None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        dni: str = payload.get("dni")
        if username is None or dni is None:
            raise credentials_exception
        return {"username": username, "dni": dni}
    except JWTError:
        raise credentials_exception

# -----------------------------------------------------------------------------
# ENDPOINTS DE LA API
# -----------------------------------------------------------------------------

@app.post("/api/auth/login", tags=["Autenticación"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No se pudo conectar.")
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s;", (form_data.username,))
        user = cursor.fetchone()
        
        if not user or not (form_data.password == user["contrasena"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nombre de usuario o contraseña incorrectos",
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["nombre_usuario"], "dni": user["dni"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        if conn:
            conn.close()


@app.get("/api/me/info", tags=["Usuario Autenticado"])
def get_my_info(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No se pudo conectar.")
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        sql = """
            SELECT c.nombre, c.apellido, cu.numerocuenta, cu.saldo
            FROM clientes c JOIN cuentas cu ON c.dni = cu.dni
            WHERE c.dni = %s;
        """
        cursor.execute(sql, (current_user["dni"],))
        user_data = cursor.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="Datos del usuario no encontrados.")
        return {
            "nombre": user_data["nombre"],
            "apellido": user_data["apellido"],
            "account_number": user_data["numerocuenta"],
            "balance": float(user_data["saldo"])
        }
    finally:
        if conn:
            conn.close()


@app.get("/api/me/movements", tags=["Usuario Autenticado"])
def get_my_movements(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No se pudo conectar.")
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT numerocuenta FROM cuentas WHERE dni = %s;", (current_user["dni"],))
        account = cursor.fetchone()
        if not account:
            raise HTTPException(status_code=404, detail="No se encontraron cuentas para este usuario.")
        account_number = account['numerocuenta']
        sql_query = """
            SELECT transaccionid, cuentaorigen, cuentadestino, monto, fecha_transaccion
            FROM transacciones WHERE cuentaorigen = %s OR cuentadestino = %s
            ORDER BY fecha_transaccion DESC LIMIT 5;
        """
        cursor.execute(sql_query, (account_number, account_number))
        results = cursor.fetchall()
        movements = [
            {"id": row["transaccionid"], "origen": row["cuentaorigen"], "destino": row["cuentadestino"], "monto": float(row["monto"]), "fecha": row["fecha_transaccion"].isoformat()}
            for row in results
        ]
        return {"movements": movements}
    finally:
        if conn:
            conn.close()
            
@app.post("/api/transfers", tags=["Transacciones"])
def execute_transfer(transfer_request: TransferRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No se pudo conectar.")
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT dni FROM cuentas WHERE numerocuenta = %s;", (transfer_request.cuenta_origen,))
        owner = cursor.fetchone()
        if not owner or owner['dni'] != current_user['dni']:
            raise HTTPException(status_code=403, detail="No tienes permiso para operar con esta cuenta de origen.")
        
        cursor.execute("CALL realizar_transferencia(%s, %s, %s);",
                       (transfer_request.cuenta_origen, transfer_request.cuenta_destino, transfer_request.monto))
        conn.commit()
        return {"status": "success", "message": "Transferencia realizada con éxito."}
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conn:
            conn.close()

def serialize_doc(doc):
    """Convierte un documento de MongoDB, incluyendo su _id, a un formato JSON compatible."""
    doc['_id'] = str(doc['_id'])
    return doc

@app.get("/api/products", tags=["Tienda"])
def get_all_products():
    """
    Obtiene la lista de todos los productos de la tienda desde MongoDB.
    """
    try:
        products_cursor = db_mongo.products.find({})
        
        products_list = [serialize_doc(product) for product in products_cursor]

        return products_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar los productos: {e}")

@app.post("/api/cart/items", tags=["Carrito de Compras"])
def add_item_to_cart(item_request: AddToCartRequest, current_user: dict = Depends(get_current_user)):
    """
    Añade un producto al carrito de compras del usuario actual.
    Si el carrito no existe, lo crea. Si el producto ya existe, actualiza la cantidad.
    """
    client_dni = current_user["dni"]
    cart_id = f"cart_dni_{client_dni}"

    try:
        # 1. BUSCAR EL PRODUCTO PARA OBTENER SUS DATOS FRESCOS
        product = db_mongo.products.find_one({"_id": ObjectId(item_request.product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        
        # 2. BUSCAR EL CARRITO EXISTENTE DEL USUARIO
        cart = db_mongo.carts.find_one({"_id": cart_id})

        if not cart:
            # 3A. SI NO HAY CARRITO, CREAMOS UNO NUEVO
            new_cart = {
                "_id": cart_id,
                "client_dni": client_dni,
                "items": [],
                "created_at": datetime.utcnow(),
            }
            cart = new_cart
        
        # 4. AÑADIR O ACTUALIZAR EL ITEM EN EL CARRITO
        item_index = -1
        for i, item in enumerate(cart["items"]):
            if item["product_id"] == ObjectId(item_request.product_id):
                item_index = i
                break

        if item_index != -1:
            # El producto ya está en el carrito, actualizamos la cantidad
            cart["items"][item_index]["quantity"] += item_request.quantity
        else:
            # El producto es nuevo, lo añadimos al array de items
            new_item = {
                "product_id": ObjectId(item_request.product_id),
                "store_id": product["store_id"],
                "sku": product["sku"],
                "name": product["name"],
                "quantity": item_request.quantity,
                "price_per_unit": float(product["price"])
            }
            cart["items"].append(new_item)

        # 5. RECALCULAR SUBTOTALES Y TOTAL
        subtotals = {} # Usaremos un diccionario para agrupar por tienda
        total_price = 0
        
        # Obtenemos la información de las tiendas en una sola consulta
        store_ids = list(set([item["store_id"] for item in cart["items"]]))
        stores_info = {
            store["_id"]: store for store in db_mongo.stores.find({"_id": {"$in": store_ids}})
        }

        for item in cart["items"]:
            store_id = item["store_id"]
            price = item["price_per_unit"] * item["quantity"]
            total_price += price
            if store_id in subtotals:
                subtotals[store_id] += price
            else:
                subtotals[store_id] = price
        
        cart["subtotals_by_store"] = [
            {
                "store_id": store_id,
                "subtotal": subtotal,
                "payout_account_number": stores_info.get(store_id, {}).get("payout_account_number", "N/A")
            }
            for store_id, subtotal in subtotals.items()
        ]
        cart["total_price"] = total_price
        cart["updated_at"] = datetime.utcnow()

        # 6. GUARDAR EL CARRITO EN LA BASE DE DATOS
        db_mongo.carts.replace_one({"_id": cart_id}, cart, upsert=True)

        return {"status": "success", "message": "Producto añadido al carrito.", "cart": serialize_cart(cart)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/api/cart", tags=["Carrito de Compras"])
def get_my_cart(current_user: dict = Depends(get_current_user)):
    """
    Obtiene y retorna el contenido del carrito de compras del usuario actual.
    Si el usuario no tiene un carrito, retorna un estado indicándolo.
    """
    client_dni = current_user["dni"]
    cart_id = f"cart_dni_{client_dni}"

    try:
        # 1. Buscamos el carrito en la base de datos usando su ID único.
        cart = db_mongo.carts.find_one({"_id": cart_id})

        if not cart:
            # 2. Si no se encuentra ningún carrito, no es un error.
            #    Simplemente significa que está vacío. Devolvemos una respuesta clara.
            return {
                "status": "success",
                "exists": False,
                "message": "El carrito está vacío."
            }
        
        # 3. Si encontramos el carrito, lo serializamos para que sea compatible con JSON
        #    (convirtiendo los ObjectId a strings) y lo devolvemos.
        return {
            "status": "success",
            "exists": True,
            "cart": serialize_cart(cart)
        }

    except Exception as e:
        # Capturamos cualquier error inesperado de la base de datos.
        raise HTTPException(status_code=500, detail=f"Error al obtener el carrito: {str(e)}")

@app.post("/api/orders", tags=["Pedidos"])
def create_order_from_cart(current_user: dict = Depends(get_current_user)):
    """
    Crea un pedido a partir del carrito del usuario.
    Orquesta la verificación de saldo y las transferencias en PostgreSQL,
    luego crea el documento de pedido y elimina el carrito en MongoDB.
    """
    client_dni = current_user["dni"]
    cart_id = f"cart_dni_{client_dni}"

    # Preparamos las conexiones a AMBAS bases de datos.
    conn_pg = get_db_connection()
    if conn_pg is None:
        raise HTTPException(status_code=503, detail="No se pudo conectar al servicio de transacciones.")

    try:
        # 1. OBTENER EL CARRITO DE MONGODB
        cart = db_mongo.carts.find_one({"_id": cart_id})
        if not cart or not cart.get("items"):
            raise HTTPException(status_code=400, detail="El carrito está vacío.")

        total_price = cart["total_price"]

        # 2. VERIFICAR SALDO EN POSTGRESQL
        cursor_pg = conn_pg.cursor(cursor_factory=RealDictCursor)
        cursor_pg.execute("SELECT numerocuenta, saldo FROM cuentas WHERE dni = %s;", (client_dni,))
        user_account = cursor_pg.fetchone()
        
        if not user_account:
            raise HTTPException(status_code=404, detail="No se encontró la cuenta del usuario.")
        
        if user_account["saldo"] < total_price:
            raise HTTPException(status_code=400, detail="Saldo insuficiente para completar la compra.")

        user_account_number = user_account["numerocuenta"]

        # 3. EJECUTAR LAS TRANSFERENCIAS (OPERACIÓN TRANSACCIONAL)
        # Iteramos sobre el resumen de pagos que ya habíamos calculado en el carrito.
        for subtotal_info in cart["subtotals_by_store"]:
            destination_account = subtotal_info["payout_account_number"]
            amount_to_transfer = subtotal_info["subtotal"]
            
            # Llamamos a nuestro confiable Stored Procedure para cada tienda
            cursor_pg.execute("CALL realizar_transferencia(%s, %s, %s);",
                              (user_account_number, destination_account, amount_to_transfer))

        # Si todas las llamadas al SP fueron exitosas, hacemos COMMIT en PostgreSQL
        conn_pg.commit()
        cursor_pg.close()

        # 4. CREAR EL DOCUMENTO DE PEDIDO EN MONGODB (REGISTRO PERMANENTE)
        order_document = {
            "order_number": f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{client_dni[-4:]}",
            "client_dni": client_dni,
            "account_number_used": user_account_number,
            "items": cart["items"],
            "payment_summary": [
                {
                    "store_id": s["store_id"],
                    "amount_transferred": s["subtotal"],
                    "destination_account": s["payout_account_number"]
                } for s in cart["subtotals_by_store"]
            ],
            "total_price": total_price,
            "status": "COMPLETADO",
            "purchase_date": datetime.utcnow()
        }
        
        db_mongo.orders.insert_one(order_document)

        # 5. LIMPIAR EL CARRITO EN MONGODB
        db_mongo.carts.delete_one({"_id": cart_id})

        return {"status": "success", "message": "¡Compra realizada con éxito!", "order_number": order_document["order_number"]}

    except Exception as e:
        # Si algo falla, especialmente las transferencias, hacemos rollback en PostgreSQL.
        if conn_pg:
            conn_pg.rollback()
        raise HTTPException(status_code=400, detail=f"Error al procesar el pedido: {str(e)}")
    finally:
        # Nos aseguramos de cerrar siempre la conexión a PostgreSQL.
        if conn_pg:
            conn_pg.close()

@app.post("/api/reviews", tags=["Reviews"])
def create_review(review_data: ReviewRequest, current_user: dict = Depends(get_current_user)):
    """
    Permite a un usuario autenticado enviar una calificación y un comentario
    sobre la experiencia en la aplicación.
    """
    # Validamos la puntuación en el backend también, por si acaso.
    if not 1 <= review_data.score <= 10:
        raise HTTPException(status_code=400, detail="La puntuación debe estar entre 1 y 10.")
        
    try:
        # Creamos el documento que se insertará en MongoDB.
        review_document = {
            "client_dni": current_user["dni"],
            "client_username": current_user["username"],
            "score": review_data.score,
            "created_at": datetime.utcnow()
        }
        
        # Añadimos el comentario solo si el usuario lo envió.
        if review_data.comment:
            review_document["comment"] = review_data.comment
        
        # Insertamos el documento en la colección 'reviews'.
        result = db_mongo.reviews.insert_one(review_document)

        return {
            "status": "success",
            "message": "¡Gracias por tu calificación!",
            "review_id": str(result.inserted_id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo guardar la calificación: {str(e)}")


# FUNCIÓN AUXILIAR para serializar el carrito completo
def serialize_cart(cart):
    """Convierte los ObjectId de un carrito a strings para la respuesta JSON."""
    if cart and "_id" in cart:
        for item in cart.get("items", []):
            if "product_id" in item:
                item["product_id"] = str(item["product_id"])
    return cart