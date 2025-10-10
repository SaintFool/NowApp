INSERT INTO clientes (dni, nombre, apellido, direccion, telefono, email) VALUES
('12345678', 'Juan', 'Pérez', 'Av. Libertador 123', '555-1234', 'juan.perez@email.com'),
('23456789', 'María', 'Gómez', 'Calle Florida 456', '555-5678', 'maria.gomez@email.com'),
('34567890', 'Carlos', 'Rodríguez', 'Av. Rivadavia 789', '555-9012', 'carlos.rod@email.com'),
('45678901', 'Ana', 'López', 'Calle Corrientes 321', '555-3456', 'ana.lopez@email.com'),
('56789012', 'Pedro', 'Martínez', 'Av. Santa Fe 654', '555-7890', 'pedro.mart@email.com'),
('67890123', 'Lucía', 'Fernández', 'Calle Córdoba 987', '555-2345', 'lucia.fer@email.com'),
('78901234', 'Miguel', 'García', 'Av. Belgrano 654', '555-6789', 'miguel.gar@email.com'),
('89012345', 'Sofía', 'Díaz', 'Calle San Martín 321', '555-0123', 'sofia.diaz@email.com'),
('90123456', 'Pablo', 'Ruiz', 'Av. Callao 789', '555-4567', 'pablo.ruiz@email.com'),
('01234567', 'Laura', 'Sánchez', 'Calle Lavalle 123', '555-8901', 'laura.san@email.com');

INSERT INTO cuentas (numerocuenta, dni, tipocuenta, saldo, fecha_apertura) VALUES
('CTAX10001', '12345678', 'Ahorro', 0, '2023-01-15'),
('CTAX10002', '23456789', 'Corriente', 0, '2023-02-20'),
('CTAX10003', '34567890', 'Ahorro', 0, '2023-03-10'),
('CTAX10004', '45678901', 'Corriente', 0, '2023-04-05'),
('CTAX10005', '56789012', 'Ahorro', 0, '2023-05-12'),
('CTAX20001', '67890123', 'Corriente', 1250.50, '2023-01-10'),
('CTAX20002', '78901234', 'Ahorro', 3789.25, '2023-02-15'),
('CTAX20003', '89012345', 'Corriente', 4200.75, '2023-03-22'),
('CTAX20004', '90123456', 'Ahorro', 150.00, '2023-04-18'),
('CTAX20005', '01234567', 'Corriente', 4950.99, '2023-05-25');

INSERT INTO usuarios (dni, nombre_usuario, contrasena) VALUES
('12345678', 'juan_perez', 'clave123'),
('23456789', 'maria_gomez', 'securepass'),
('34567890', 'carlos_rod', 'password1'),
('45678901', 'ana_lopez', 'miclave456'),
('56789012', 'pedro_mart', 'abc123xyz'),
('67890123', 'lucia_fer', 'lucia2023'),
('78901234', 'miguel_gar', 'miguelpass'),
('89012345', 'sofia_diaz', 'sofia1234'),
('90123456', 'pablo_ruiz', 'pablo2023'),
('01234567', 'laura_san', 'laura5678');