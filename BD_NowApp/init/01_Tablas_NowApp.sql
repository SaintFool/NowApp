CREATE TABLE clientes (
    dni VARCHAR(8) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    telefono VARCHAR(15),
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE cuentas (
    numerocuenta VARCHAR(20) PRIMARY KEY,
    dni VARCHAR(8) NOT NULL REFERENCES clientes(dni) ON DELETE RESTRICT,
    tipocuenta VARCHAR(50) NOT NULL,
    saldo DECIMAL(15, 2) NOT NULL DEFAULT 0.00 CHECK (saldo >= 0),
    fecha_apertura DATE NOT NULL DEFAULT CURRENT_DATE,
    estado VARCHAR(10) NOT NULL DEFAULT 'ACTIVA' CHECK (estado IN ('ACTIVA', 'INACTIVA', 'BLOQUEADA'))
);

CREATE TABLE usuarios (
    usuarioid SERIAL PRIMARY KEY,
    dni VARCHAR(8) NOT NULL UNIQUE REFERENCES clientes(dni) ON DELETE RESTRICT,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    contrasena VARCHAR(100) NOT NULL
);

CREATE TABLE transacciones (
    transaccionid SERIAL PRIMARY KEY,
    cuentaorigen VARCHAR(20) NOT NULL REFERENCES cuentas(numerocuenta) ON DELETE RESTRICT,
    cuentadestino VARCHAR(20) NOT NULL REFERENCES cuentas(numerocuenta) ON DELETE RESTRICT,
    monto DECIMAL(15, 2) NOT NULL CHECK (monto > 0),
    fecha_transaccion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (cuentaorigen <> cuentadestino)
);