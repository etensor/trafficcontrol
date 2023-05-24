import json
import plotly.graph_objects as go
from dash import Dash, dcc, html, Output, Input


fig = go.Figure(go.Sunburst(
    ids=[
        "Activity 1", "Activity 2", "Activity 3", "Sub-Activity 1", "Sub-Activity 2",
        "Sub-Activity 3", "Sub-Activity 4", "Sub-Activity 5", "Sub-Activity 6"
    ],
    labels=[
        "Activity 1", "Activity 2", "Activity 3", "Sub-Activity 1", "Sub-Activity 2",
        "Sub-Activity 3", "Sub-Activity 4", "Sub-Activity 5", "Sub-Activity 6"
    ],
    parents=[
        "", "", "", "Activity 1", "Activity 1", "Activity 2", "Activity 2", "Activity 3", "Activity 3"
    ],
    marker=dict(
        colors=[
            "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3", "#FF6692", "#B6E880", "#FF97FF"
        ]
    )
))
fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Cronograma"),
    dcc.Graph(id='graph', figure=fig)
])


@app.callback(
    Output("graph", "figure"),
    Input("graph", "figure"))
def display_cronograma(figure):
    return json.loads(json.dumps(figure))


app.run_server(debug=True)