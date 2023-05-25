# author: llm - copilot

# Clase que representa una actividad

class Actividad:
    def __init__(self, name, text="", children=None, value=0):
        self.name = name
        self.text = text
        self.children = children or []
        self.value = value

    def to_dict(self):
        return {
            "name": self.name,
            "text": self.text,
            "children": [child.to_dict() for child in self.children],
            "value": self.value
        }

    # Crear una actividad a partir de un diccionario
    @classmethod
    def from_dict(cls, data):
        children = [cls.from_dict(child_data) for child_data in data.get("children", [])]
        return cls(
            name=data["name"],
            text=data.get("text", ""),
            children=children,
            value=data.get("value", 0)
        )

   
def act2dict(activity):
    # Create a dictionary with the activity's attributes
    activity_dict = {
        "name": activity.name,
        "text": activity.text,
        "value": activity.value
    }

    # If the activity has children, add them to the dictionary recursively
    if hasattr(activity, "children") and activity.children:
        activity_dict["children"] = [act2dict(child) for child in activity.children]

    return activity_dict