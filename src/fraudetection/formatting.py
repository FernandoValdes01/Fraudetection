"""Formato numérico español para mensajes y presentaciones."""


def es_number(value, digits=0):
    """Devuelve miles con punto y decimales con coma; `None` representa un límite libre."""
    if value is None:
        return "libre"
    integer, _, fraction = f"{float(value):,.{digits}f}".partition(".")
    integer = integer.replace(",", ".")
    return f"{integer},{fraction}" if fraction else integer
