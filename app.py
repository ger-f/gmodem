import os
import datetime

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import pandas as pd
from colour import Color

from gmodemdata import PacketGetter
from server import app, server
from plotly import graph_objs as go

from lib.app_layout import footer, header

# TODO:
# 1 - lerp colours as a function of time
# 2 - poll data to update it
# 3 - add header/footer + css
# 4 - add graphes


# Fixes to do
# 1 remove undo on new update
# 2 fix
# 3 add css

colors = dict(col_a = Color('#f79b4b'), # Orange
                col_b = Color('#589EA5'), # Teal
                orange='#f79b4b',
                teal='#589EA5',
                purple='#660066',
                purple_two='#7A75A8',
                green='#198C70'
                    )
plotly_config = dict(displayModeBar=False)

global_df = pd.DataFrame(PacketGetter().packets)

def init_map():
    zoom = 7
    bearing = 0
    lat_centre = 31.77996
    lon_centre = -95.71689
    data = [
        go.Scattermapbox(
            lat=[lat_centre],
            lon=[lon_centre],
            mode='markers',
            marker=dict(
                size=14
            ),
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
                lat=lat_centre,
                lon=lon_centre,
            ),
            # style='dark',
            bearing=bearing,
            zoom=zoom
        ),
    )

    return go.Figure(layout=layout, )

def make_summary_data(d={}):
    style = {'padding': '5px', 'fontSize': '16px'}
    time = d.get('emailtime','-')
    return [
        html.Span('Last packet received: {}'.format(time), style=style),
        html.Span('Current Longitude: {0:.2f}'.format(d.get('lon', 0.0)), style=style),
        html.Span('Current Latitude: {0:.2f}'.format(d.get('lat', 0.0)), style=style),
        html.Span('Current Altitdue: {0:.2f}'.format(d.get('alt', 0.0)), style=style),
        html.Span('Bias Voltage: {0:.2f}'.format(d.get('volts', 0.0)), style=style),
        html.Span('ASIC Status: {}'.format(d.get('asicstate', 0.0)), style=style),
        html.Span('SIPHRA Status: {}'.format(d.get('siphrastate', 0.0)), style=style),
        html.Span('Flight Status: {}'.format(d.get('flightstate', 0.0)), style=style),]

app.layout=html.Div(id='container', className='background',
    children=[
        html.Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
        html.Meta(
            name='description',
            content=('GMoDem 2018 Flight Dashboard')
        ),
        header,
        html.Div(className='content-container', children=[
            html.Div(className='section-container', children=[
                html.Div(id='summary_div', children=make_summary_data(), className='container-width',
                ),
            ]),
            html.Hr(),
            html.Div(className='section-container', children=[
                html.Div(id='map_div',
                    children=dcc.Graph(id='map-graph', figure=init_map(), config=plotly_config),
                ),
            ]),
            html.Hr(),
            html.Div(className='section-container', children=[
                html.Div(id='temp_div',
                    children=dcc.Graph(id='temp-graph', config=plotly_config)
                    ),
                html.Div(id='count_div',
                    children=dcc.Graph(id='count-graph', config=plotly_config)
                    ),
            ]),
            dcc.Interval(
                id='interval-component',
                interval=60*1e3,
                n_intervals=0
            ),
            html.Div(hidden=True, id='hidden-div'),
        ]),
        footer,
    ],
)

def load_json(json):
    return pd.read_json(json)

# Save data to hidden json
@app.callback(Output('hidden-div', 'children'),
                [Input('interval-component', 'n_intervals')])
def test(n):
    # print('checking for new packets')
    df = global_df.sort_values(by='emailtime')
    df['emailtime'] = pd.to_datetime(df['emailtime']).dt.strftime('%Y-%m-%d %H:%M:%S')
    return df.to_json()
    if n%2:
        return global_df.to_json()
    else:
        return global_df[:1].to_json()

# Update summary row
@app.callback(Output('summary_div', 'children'),
                [Input('hidden-div', 'children')],)
def update_topbar(json):
    df = load_json(json).sort_values(by='emailtime')
    return make_summary_data(d=df.iloc[-1])

# Update temperature graph
@app.callback(Output('temp-graph', 'figure'),
                [Input('hidden-div', 'children')],)
def update_topbar(json):
    df = load_json(json)
    data = [
        go.Scatter(x = df.emailtime, y=df.sipmtemp,
                name='SiPM',
                marker=go.Marker(
                    color=colors['teal']
                )
            ),
        go.Scatter(x = df.emailtime, y=df.inttemp,
                name='Interior',
                marker=go.Marker(
                    color=colors['orange']
                )
            ),
        go.Scatter(x = df.emailtime, y=df.exttemp,
                name='Exterior',
                marker=go.Marker(
                    color=colors['purple_two']
                )
            ),
        ]

    layout = go.Layout(
        title='Temperatures',
        yaxis=dict(
            title=u'℃'
        ),
        yaxis2=dict(
            title='m',
            titlefont=dict(
                color=colors['orange']
            ),
            tickfont=dict(
                color=colors['orange']
            ),
            overlaying='y',
            side='right'
        ),
    )
    return go.Figure(data=data, layout=layout)

# Update Count/Alt graph
@app.callback(Output('count-graph', 'figure'),
                [Input('hidden-div', 'children')],)
def update_topbar(json):
    df = load_json(json)
    data = [
        go.Scatter(x = df.emailtime, y=df.counts,
                name='Count Rate (Hz)',
                marker=go.Marker(
                    color=colors['teal'],
                )
            ),
        go.Scatter(x = df.emailtime, y=df.alt,
                name='Altitude',
                marker=go.Marker(
                    color=colors['orange']
                ),
                yaxis='y2'
            ),
        ]

    layout = go.Layout(
        title='Detector Count Rate and Balloon Altitude',
        yaxis=dict(
            title='counts/s'
        ),
        yaxis2=dict(
            title='m',
            titlefont=dict(
                color=colors['orange']
            ),
            tickfont=dict(
                color=colors['orange']
            ),
            overlaying='y',
            side='right'
        ),
    )

    return go.Figure(data=data, layout=layout)


@app.callback(Output('map-graph', 'figure'),
                [Input('hidden-div', 'children')],
                [State('map-graph', 'relayoutData')])
def update_map(json, relayout_data):
    df = load_json(json)

    zoom = 7
    bearing = 0
    lat_centre = 31.77996
    lon_centre = -95.71689

    if relayout_data is not None:
        if 'mapbox' in relayout_data:
            mpbox = relayout_data['mapbox']
            lat_centre = float(mpbox['center']['lat'])
            lon_centre = float(mpbox['center']['lon'])
            bearing = float(mpbox['bearing'])
            zoom = float(mpbox['zoom'])

    data = [
        go.Scattermapbox(
            lat=df.lat,
            lon=df.lon,
            mode='markers',
            marker=dict(
                size=14,
                cmin=df.alt.min(),
                cmax=df.alt.max(),
                color=df.alt,
                colorbar=dict(title='Altitude (m)'),
                colorscale='Viridis'
            ),
            text=df.time,
        )
    ]

    layout = go.Layout(
        autosize=False,
        height=750,
        margin=go.Margin(l=0, r=0, t=0, b=0),
        showlegend=False,
        mapbox=dict(
            accesstoken=os.environ['MAPBOX_TOKEN'],
            center=dict(
                lat=lat_centre,
                lon=lon_centre,
            ),
            style='dark',
            bearing=bearing,
            zoom=zoom
        ),
    )

    return go.Figure(data=data, layout=layout)


css = ['https://codepen.io/ger-ie/pen/XYOmLZ.css',
       'https://codepen.io/ger-ie/pen/LrqpKX.css',
       'https://codepen.io/ger-ie/pen/mKveZN.css',]

app.css.append_css({
    'external_url': (
                css[0],
                css[1],
                css[2],
                'https://fonts.googleapis.com/css?family=Michroma',)
    })

# app.scripts.config.serve_locally = True

if __name__ == '__main__':
    app.run_server(debug=True, port=8001)
