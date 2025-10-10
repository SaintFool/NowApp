CREATE OR REPLACE PROCEDURE realizar_transferencia(
    IN p_cuenta_origen VARCHAR(20),
    IN p_cuenta_destino VARCHAR(20),
    IN p_monto DECIMAL(15, 2)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_saldo_origen DECIMAL(15, 2);
    v_estado_origen VARCHAR(10);
    v_estado_destino VARCHAR(10);
BEGIN
    -- Validaciones iniciales
    IF p_cuenta_origen = p_cuenta_destino THEN
        RAISE EXCEPTION 'No puedes transferir a la misma cuenta';
    END IF;

    IF p_monto <= 0 THEN
        RAISE EXCEPTION 'El monto debe ser positivo';
    END IF;

    -- Bloquear filas para evitar condiciones de carrera
    PERFORM 1 FROM cuentas 
    WHERE numerocuenta IN (p_cuenta_origen, p_cuenta_destino)
    FOR UPDATE;

    -- Obtener saldo y estado de cuenta origen
    SELECT saldo, estado INTO v_saldo_origen, v_estado_origen
    FROM cuentas 
    WHERE numerocuenta = p_cuenta_origen;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Cuenta origen no encontrada';
    END IF;

    -- Verificar cuenta destino
    SELECT estado INTO v_estado_destino
    FROM cuentas 
    WHERE numerocuenta = p_cuenta_destino;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Cuenta destino no encontrada';
    END IF;

    -- Validar estado de las cuentas
    IF v_estado_origen <> 'ACTIVA' THEN
        RAISE EXCEPTION 'La cuenta origen está inactiva o bloqueada';
    END IF;

    IF v_estado_destino <> 'ACTIVA' THEN
        RAISE EXCEPTION 'La cuenta destino está inactiva o bloqueada';
    END IF;

    -- Verificar fondos suficientes
    IF v_saldo_origen < p_monto THEN
        RAISE EXCEPTION 'Saldo insuficiente. Saldo actual: %', v_saldo_origen;
    END IF;

    -- Realizar la transferencia
    UPDATE cuentas
    SET saldo = saldo - p_monto
    WHERE numerocuenta = p_cuenta_origen;

    UPDATE cuentas
    SET saldo = saldo + p_monto
    WHERE numerocuenta = p_cuenta_destino;

    INSERT INTO transacciones (
        cuentaorigen, 
        cuentadestino, 
        monto, 
        fecha_transaccion
    ) VALUES (
        p_cuenta_origen,
        p_cuenta_destino,
        p_monto,
        CURRENT_TIMESTAMP
    );

    -- Notificar éxito
    RAISE NOTICE 'Transferencia exitosa de % de % a %', p_monto, p_cuenta_origen, p_cuenta_destino;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error en la transferencia: %', SQLERRM;
END;
$$;