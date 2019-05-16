import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
#import dash-bootstrap-components
import json
import plotly
from plotly import graph_objs as go
from plotly.graph_objs import *
import pandas as pd
from sqlalchemy import create_engine
import yaml

#############
# ENV SETUP #
#############
config = yaml.safe_load(open("config.yaml"))

# postgresql db connection
# CREATEENGINE = config['postgresql']['CREATEENGINE']

###################
# create connection
###################
# engine = create_engine(CREATEENGINE)
# sql = 'SELECT lot, sq_feet, geom from public.lots_table order by lot;'

# gdf = gpd.GeoDataFrame.from_postgis(sql, con=engine, geom_col='geom' )

mapbox_access_token = config['MAPBOX']['TOKEN']

df  = pd.read_csv('./data/parkinglots_simplified_centroid_4326.csv')
site_lat = list(df['lat'])
site_lon = list(df['lon'])
locations_name = list(df['lot'])

#external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheet)
app = dash.Dash()
app.scripts.config.serve_locally=True

app.layout = html.Div([
    html.H4('FPDCC Parking Lots'),
    html.Div([
        html.Div([
            dcc.Graph(
            	id = 'map',
            	figure = {
            		'data': [ go.Scattermapbox(
                        lat = site_lat,
            		    lon = site_lon,
                        mode = 'markers',
                        marker = {
                            'size':10,
                            'color':'#265465',
                        }
                    )],
            		'layout': go.Layout(
                        hovermode = "closest",
            			height = 800,
            			autosize = True,
            			mapbox = dict(
            				accesstoken = mapbox_access_token,
            				center = {'lat' : 41.808611,'lon' : -87.888889},
            		        zoom = 9,
            		        style = 'light'
                        )
                    )
            	}
            )], className = 'six columns'),
        html.Div([
            dcc.Graph(
                id = 'graph-lots'
            )
    ], className = 'six columns')
    ], className = 'row'),

    html.Div([
        dt.DataTable(
            id = 'datatable-lots',
            data=df.to_dict("rows"),
            #rows = df.to_dict('records'),
            columns = sorted(df.columns.difference(['geom'])),
            editable=True,
            filtering=True,
            sorting=True,
            sorting_type="multi",
            row_selectable="multi",
            row_deletable=True,
            selected_rows=[]
        )
    ]),
], className = "container")

@app.callback(
    Output('datatable-lots', 'selected_rows'),
    [Input('graph-lots', 'clickData')],
    [State('datatable-lots', 'selected_rows')])
def update_selected_rows(clickData, selected_rows):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_rows:
                selected_rows.remove(point['pointNumber'])
            else:
                selected_rows.append(point['pointNumber'])
    return selected_rows


@app.callback(
    Output('graph-lots', 'figure'),
    [Input('datatable-lots', 'data'),
     Input('datatable-lots', 'selected_rows')])
def update_figure(data, selected_rows):
    dff = pd.DataFrame(data)
    data = [go.Bar(
            x = dff['lot'],
            y = dff['sqft'],
            width = 1,
            name = 'Lot Square Feet'
            )
        ]
    fig = go.Figure(data=data)
    return fig


#app.css.append_css({
#    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
#})


if __name__ == '__main__':
    app.run_server(debug=True)
