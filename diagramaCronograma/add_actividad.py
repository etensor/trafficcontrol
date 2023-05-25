''' # Ejemplo de uso
    # Añade una nueva actividad al diagrama de sol, al segundo nivel

    # # # Ilogico complicarse asi

data = add_level(
    data=data,
    parent_name="Actividad 2",
    level_name="Sub-Actividad 7",
    level_text="This is the seventh sub-activity",
    level_children=[],
    level_value=10
)'''

def add_level(data, parent_name, level_name, level_text, level_children, level_value):
    """
    Agrega un nuevo nivel al diagrama de sol.

    Args:
        data (dict): Los datos existentes del diagrama de sol.
        parent_name (str): El nombre del nivel padre.
        level_name (str): El nombre del nuevo nivel.
        level_text (str): El texto para mostrar en el nuevo nivel.
        level_children (list): Los hijos del nuevo nivel.
        level_value (int): El valor del nuevo nivel.

    Returns:
        dict: Los datos actualizados del diagrama de sol.
    """
    # Busca el nivel padre en los datos

    parent_level = None
    for level in data["children"]:
        if level["name"] == parent_name:
            parent_level = level
            break

    # Si no se encontró el nivel padre, genera un error
    if parent_level is None:
        raise ValueError(f"Nivel padre '{parent_name}' no encontrado en los datos")

    # Agrega el nuevo nivel a los hijos del nivel padre
    new_level = {
        "name": level_name,
        "text": level_text,
        "children": level_children,
        "value": level_value
    }
    parent_level["children"].append(new_level)

    # Devuelve los datos actualizados
    return data
