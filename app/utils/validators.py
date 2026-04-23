def validar_cedula_ecuatoriana(cedula: str) -> bool:
    
    if not cedula.isdigit() or len(cedula) != 10:
        return False

    provincia = int(cedula[0:2])
    if provincia < 1 or provincia > 24:
        return False

    tercer_digito = int(cedula[2])
    if tercer_digito >= 6:
        return False

    suma = 0

    for i in range(9):
        num = int(cedula[i])

        if i % 2 == 0:  # posiciones impares (0-index)
            num *= 2
            if num > 9:
                num -= 9

        suma += num

    decena = ((suma // 10) + 1) * 10
    digito_verificador = decena - suma

    if digito_verificador == 10:
        digito_verificador = 0

    return digito_verificador == int(cedula[9])