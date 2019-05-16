import dash
import json
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import geopandas as gpd

#############
# ENV SETUP #
#############
config = yaml.safe_load(open("config.yaml"))

mapbox_access_token = config['MAPBOX']['TOKEN']

app = dash.Dash()
app.scripts.config.serve_locally=True

gdf  = gpd.read_file( './data/parkinglots_simplified_4326.geojson')

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
					source     = json.loads( gdf.to_json() )
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
