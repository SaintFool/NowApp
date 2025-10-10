import psycopg2
from passlib.context import CryptContext

# Configuración de la Base de Datos (igual que en main.py)
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "BD_Transaccional_NowApp"
DB_USER = "admin"
DB_PASSWORD = "una_contraseña_muy_fuerte_123"

# 1. Creamos un contexto de hasheo, especificando que usaremos el algoritmo bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_existing_passwords():
    conn = None
    try:
        conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' port='{DB_PORT}' password='{DB_PASSWORD}'"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        # 2. Obtenemos todos los usuarios y sus contraseñas en texto plano.
        cursor.execute("SELECT usuarioid, contrasena FROM usuarios;")
        users = cursor.fetchall()

        print(f"Encontrados {len(users)} usuarios para actualizar.")

        for user in users:
            user_id, plain_password = user
            
            # ¡OJO! Solo hasheamos si la contraseña no parece ya un hash de bcrypt.
            if not plain_password.startswith('$2b$'):
                # 3. Hasheamos la contraseña en texto plano.
                hashed_password = pwd_context.hash(plain_password)
                print(f"Actualizando usuario {user_id}: {plain_password} -> {hashed_password[:30]}...")
                
                # 4. Actualizamos la fila en la base de datos con la contraseña hasheada.
                cursor.execute(
                    "UPDATE usuarios SET contrasena = %s WHERE usuarioid = %s;",
                    (hashed_password, user_id)
                )
            else:
                print(f"Usuario {user_id} ya tiene una contraseña hasheada. Omitiendo.")

        conn.commit()
        cursor.close()
        print("\n¡Todas las contraseñas han sido hasheadas y actualizadas con éxito!")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"ERROR: {e}")
    finally:
        if conn:
            conn.close()

# Ejecutamos la función
if __name__ == "__main__":
    hash_existing_passwords()