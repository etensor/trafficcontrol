import json
import plotly.graph_objects as go
from dash import Dash, dcc, html, Output, Input
import dash_bootstrap_components as dbc
from actividades import data_actividades, marker_colors


data = data_actividades

#### Diagrama de Sunburst

parents = ["Cronograma"] * len(data["children"])
for i, activity in enumerate(data["children"]):
    if "children" in activity:
        for sub_activity in activity["children"]:
            parents.append(activity["name"])
    else:
        parents.append("Cronograma")

fig = go.Figure(go.Sunburst(
    labels=[node["name"] for node in data["children"]] + \
        [node["name"] for activity in data["children"] \
        if "children" in activity for node in activity["children"]],
    parents=parents,
    values=[node["value"] for node in data["children"]] + [node["value"] for activity in data["children"] if "children" in activity for node in activity["children"]],
    ids=[node["name"] for node in data["children"]] + [node["name"] for activity in data["children"] if "children" in activity for node in activity["children"]],
    text=[node.get("text", "") for node in data["children"]] + [node.get("text", "") for activity in data["children"] if "children" in activity for node in activity["children"]],
    hovertemplate='<b>%{label}</b><br> ↩ %{parent}<br><br>&nbsp;&nbsp;<i>%{text}</i><extra></extra>',
    textfont=dict(
        color="white",
        family="Open Sans"
    ),
    marker=dict(
        colors=marker_colors
    ),
    textinfo="label",
    #textinfo="label+text",  ## descomentar y comentar arriba para mostrar la descripción por fuera.
    hoverlabel=dict(
        bgcolor="white",
        font_size=16,
        #font_family="Grativas One",
        #bordercolor="green",
        align="left"
    ),
    #insidetextorientation='radial',
    #texttemplate='%{label}<br>',

))


fig.update_layout(
    width=1200,height=900,
    margin=dict(autoexpand=True,t=0, l=10, r=0, b=0),
    font=dict(size=16),
    template="plotly_dark",
    hovermode="x",
    #uniformtext=dict(minsize=12, mode='hide'),
    )



app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div(
    children=[
        html.H1("Cronograma", style={"text-align": "center"}),
        html.Div(
            style={
                "display": "flex",
                "justify-content": "center",
                "align-items": "center"
            },
            children=[
                dcc.Graph(id='graph', figure=fig)
            ]
        )
    ]
)


@app.callback(
    Output("graph", "figure"),
    Input("graph", "figure"))
def display_cronograma(figure):
    return json.loads(json.dumps(figure))


app.run_server(debug=True)