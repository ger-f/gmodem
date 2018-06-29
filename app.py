import os

import dash_html_components as html
import dash_core_components as dcc
import pandas as pd

import gmodemdata
from server import app, server
from plotly import graph_objs as go


# TODO:
# 1 - lerp colours as a function of time
# 2 - poll data to update it
# 3 - add header/footer + css
# 4 - add graphes


packets = gmodemdata.get_latest_packets()
df = pd.DataFrame(packets)

def make_map():
    data = [
        go.Scattermapbox(
            lat=df.lat,
            lon=df.lon,
            mode='markers',
            marker=dict(
                size=14
            ),
            text=df.time,
        )
    ]

    layout = go.Layout(
        autosize=True,
        height=750,
        margin=go.Margin(l=0, r=0, t=0, b=0),
        showlegend=False,
        mapbox=dict(
            accesstoken=os.environ['MAPBOX_TOKEN'],
            center=dict(
                lat=df.lat[0],
                lon=df.lon[0]
            ),
            # style='dark',
            bearing=0,
            zoom=7
        ),
    )
    return dcc.Graph(figure=go.Figure(data=data, layout=layout),
                        id='map-graph')

def make_header():
    return html.Div(html.H1('Headdder'), className='header')

def make_footer():
    return html.Div(html.H1('Footer'), className='footer')

app.layout=html.Div(
    children=[
        make_header(),
        html.H1('Dashiest of Boards'),
        html.Div(' '.join(df.columns)),
        html.Div(id='map_div',
            children=[make_map()],
        ),
        html.Div(id='temp_div',
            children=dcc.Graph(id='temp-graph')
            ),
        html.Div(id='count_div',
            children=dcc.Graph(id='count-graph')
            ),
        html.Div(id='bias_div',
            children=dcc.Graph(id='bias-graph')
            ),
        make_footer(),
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8001)
