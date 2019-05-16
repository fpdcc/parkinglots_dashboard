import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import json
import plotly
import plotly.graph_objs as go
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
import yaml

#############
# ENV SETUP #
#############
config = yaml.safe_load(open("config.yaml"))

# postgresql db connection
CREATEENGINE = config['postgresql']['CREATEENGINE']
EPSG = '4326'

###################
# create connection
###################
engine = create_engine(CREATEENGINE)
sql = 'SELECT lot, sq_feet, geom from public.lots_table order by lot;'

gdf = gpd.GeoDataFrame.from_postgis(sql, con=engine, geom_col='geom')
gdf_4326 = gdf.to_crs(epsg=EPSG)

app = dash.Dash()
app.scripts.config.serve_locally=True

mapbox_access_token = config['MAPBOX']['TOKEN']

app.layout = html.Div( [ dcc.Graph(
	id = 'map',
	figure = dict(
		data = [dict(
			type = 'scattermapbox'
		)],
		layout = dict(
			height   = 900,
			autosize = True,
			mapbox 	 = dict(
				layers =[dict(

					sourcetype = 'geojson',
					type 	   = 'fill',
					color	   = '#265465',
					source     = json.loads( gdf_4326.to_json() )
				)],
				accesstoken = mapbox_access_token,
				center  = dict(
		            lat = 41.808611,
		            lon = -87.888889
		        ),
		        zoom = 9,
		        style='light'
			)
		)
	)
)])

if __name__ == '__main__':
    app.run_server(debug=True)
