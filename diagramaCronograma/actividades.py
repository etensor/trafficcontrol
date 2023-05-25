from actividad import Actividad, act2dict


activity1 = Actividad(
    name="1. Investigación y reflexión",
    text="Especificar las estrategias y algoritmos ya implementados que estén relacionados con la gestión de tráfico vehicular.",
    children=[
        Actividad(
            name="Análisis de fuentes",
            text="Realizar un análisis de fuentes documentales detalladas sobre las estrategias y algoritmos utilizados en la gestión de tráfico vehicular.",
            value=30
        ),
        Actividad(
            name="Identificar propuestas acordes",
            text="Identificar y analizar las soluciones propuestas en la literatura científica para la optimización de tiempos en los semáforos.",
            value=20
        ),
        Actividad(
            name="Comparación de soluciones",
            text="Comparar las soluciones existentes en términos de eficiencia, aplicabilidad y escalabilidad.",
            value=10
        )
    ],
    value=30
)

activity2 = Actividad(
    name="2. Diseño de la solución",
    text="Diseñar un algoritmo que determine los tiempos adecuados para los estados de funcionamiento de los semáforos.",
    children=[
        Actividad(
            name="Estudio de técnicas de optimización",
            text="Estudiar los enfoques y técnicas de optimización de aprendizaje automático aplicables hacia el problema de los semáforos inteligentes.",
            value=25
        ),
        Actividad(
            name="Selección de algoritmo óptimo",
            text="Seleccionar el algoritmo óptimo a usar en base a los enfoques estudiados.",
            value=10,
        ),
        Actividad(
            name="Definición de dependencias",
            text="Establecer dependencias necesarias para la implementación del algoritmo.This is the sixth sub-activity",
            value=7
        )
    ],
    value=20
)

activity3 = Actividad(
    name="3. Implementación",
    text="Implementar un modelo de simulación que integre el algoritmo de semáforos inteligentes.",
    children=[
        Actividad(
            name="Estudio de herramientas de simulación",
            text="Identificar y seleccionar una herramienta de simulación apropiada para la implementación del modelo.",
            value=20
        ),
        Actividad(
            name="Implementación del modelo",
            text="Crear un entorno de simulación que represente de manera precisa la infraestructura vial y el tráfico en la cuidad.",
            value=15
        ),
        Actividad(
            name="Integración del algoritmo",
            text="Integrar el algoritmo de semáforos inteligentes en el modelo de simulación.",
            value=10
        )
    ],
    value=30
)

activity4 = Actividad(
    name="4. Evaluación y análisis",
    text="Evaluar el impacto de la solución propuesta mediante un caso de estudio.",
    children=[
        Actividad(
            name="Caso de estudio",
            text="Seleccionar una intersección o zona en especifica de la ciudad de Cali como caso de estudio.",
            value=10
        ),
        Actividad(
            name="Recopilación y análisis de datos",
            text="Recopilar y analizar datos de tráfico en la intersección o zona seleccionada.",
            value=10
        ),
        Actividad(
            name="Evaluación de la solución",
            text="Aplicar el modelo de simulación con semáforos inteligentes al caso de estudio para así poder obtener los resultados.",
            value=10
        ),
        Actividad(
            name="Comparación de resultados",
            text="Comparar el rendimiento de la solución propuesta con el sistema actual de semáforos en términos de tiempo de espera y flujo vehicular.",
            value=10
        ),
        Actividad(
            name="Identificación de mejoras",
            text="Identificar posibles mejorar y limitaciones de la solución propuesta en función de los resultados obtenidos.",
            value=15
        )

    ],
    value=15
)






# Conversiones
activity1_dict = act2dict(activity1)
activity2_dict = act2dict(activity2)
activity3_dict = act2dict(activity3)
activity4_dict = act2dict(activity4)




data_actividades = {
    "name": "Cronograma",
    "children": [
        activity1_dict,
        activity2_dict,
        activity3_dict,
        activity4_dict
    ]
}

marker_colors = ["#1f77b4", "#e7c526", "#2ca02c","#d62728"]