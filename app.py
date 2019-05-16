import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import json
import plotly
from plotly import graph_objs as go
from plotly.graph_objs import *
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import yaml

#external_stylesheet = ['https://codepen.io/glw/pen/Mzxpax.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheet)
app = dash.Dash()
app.scripts.config.serve_locally=True

#############
# ENV SETUP #
#############
config = yaml.safe_load(open("config.yaml"))

mapbox_access_token = config['MAPBOX']['TOKEN']

# postgresql db connection
# CREATEENGINE = config['postgresql']['CREATEENGINE']

###################
# create connection
###################
# engine = create_engine(CREATEENGINE)
# sql = 'SELECT lot, sq_feet, geom from public.lots_table order by lot;'

# gdf = gpd.GeoDataFrame.from_postgis(sql, con=engine, geom_col='geom' )

df  = pd.read_csv('./data/parkinglots_simplified_centroid_4326_v2.csv')

# Values for dropdown
zones = df['zone'].unique()
zones = np.append(zones, ['All'])

layout = dict(
    autosize=True,
    height=800,
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    legend=dict(font=dict(size=10), orientation='h'),
    title='Parking Lots',
    mapbox = dict(
        accesstoken = mapbox_access_token,
        center = dict(
            lat = 41.808611,
            lon = -87.888889
        ),
        zoom = 9,
        style = 'light'
    )
)

def gen_map(df):
    return {
        "data": [
                {
                    "type": "scattermapbox",
                    "text": list(df['lot_id']),
                    "lat": df['lat'],
        		    "lon": df['lon'],
                    "mode": "markers",
                    "name": list(df['sqft']),
                    "marker": {
                        "size": 8,
                        "opacity": 0.8,
                        "color": '#265465'
                    }
                }
            ],
        "layout": layout
    }

app.layout = html.Div([
    html.H4('FPDCC \Parking Lots'),
    html.Div([
        dcc.Dropdown(
            id='yaxis',
            options=[{'label': i.title(), 'value': i} for i in zones],
            value='All'
        )
    ],style={'width': '48%', 'float': 'left', 'display':'inline-block', 'padding-bottom': '5px'}),
    html.Button(
        id='submit-button',
        n_clicks=0,
        children='Submit',
        style={'fontSize':18, 'display':'inline-block'}
    ),
    html.Div([
        dcc.Graph(
        	id = 'map',
        	figure = gen_map(df)
        )
    ]),


        html.Div([
            dcc.Graph(id = 'graph-lots')
    ], style={'margin': 0, 'height': 900, 'height': '33%'}),

    html.Div([
        dt.DataTable(
            id = 'datatable-lots',
            data = df.to_dict('records'),
            columns = sorted(df.columns.difference(['geom'])),
            row_selectable="multi",
            sorting=True,
            filtering=True,
            selected_rows=[],
        )
    ], style={'margin': 0, 'width':'100%', 'height': '33%', 'verticalAlign':'top'}),

    html.Div(id = 'selected-indexes'),

],style={'width': '90%','height': '90%'})

# Dropdown and submit button callback to DataTable
@app.callback(
    Output('datatable-lots', 'data'),
    [Input('submit-button', 'n_clicks')],
    [State('yaxis', 'value')])
def zone_parkinglots(submitbutton, value):
    if value == 'All':
        data = df.to_dict('records')
    else:
        dff = df[df['zone'] == value]
        data = dff.to_dict('records')
        print(type(data))
        print(data)
    return data

# draw map on new dropdown selection
@app.callback(
    Output('map', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('yaxis', 'value')])
def map_update(submitbutton, value):
    if value == 'All':
        dff = df
    else:
        dff = df[df['zone'] == value]
    return gen_map(dff)

#
@app.callback(
    Output('datatable-lots', 'selected_rows'),
    [Input('graph-lots', 'clickData')],
    [State('datatable-lots', 'selected_rows')])
def update_selected_row_indices(clickData, selected_rows):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_rows:
                selected_rows.remove(point['pointNumber'])
            else:
                selected_rows.append(point['pointNumber'])
    return selected_rows

# Update bar graph based on DataTable
@app.callback(
    Output('graph-lots', 'figure'),
    [Input('datatable-lots', 'data'),
     Input('datatable-lots', 'selected_rows')])
def update_figure(data, selected_rows):
    dff = pd.DataFrame(data)
    data = [go.Bar(
            x = dff['lot_id'],
            y = dff['sqft'],
            width = 3,
            name = 'Lot Square Feet'
            )
        ]
    fig = go.Figure(data=data)
    return fig


#app.css.append_css({
#    'external_url': 'https://codepen.io/glw/pen/Mzxpax.css'
#})


if __name__ == '__main__':
    app.run_server(debug=True)
