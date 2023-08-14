import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

class Utils:
    
    def __init__(self, dataset_dir = "dataset/"):    
        self.london_stations_df = pd.read_csv(os.path.join(dataset_dir,"stations.csv"))
        self.london_connections_df = pd.read_csv(os.path.join(dataset_dir,"connections.csv"))
        self.london_lines_df = pd.read_csv(os.path.join(dataset_dir,"lines.csv"))


    def get_all_station_names(self):
        return self.london_stations_df['name'].tolist()

    def remove_spl_chars(self, text):
        return text.lower().replace(" ", "_").replace("'", "").replace("(", "_").replace(")", "_").replace("&", "and").replace(".", "").replace(",", "")

    def parse_route_by_prolog_name(self, prolog_name):
        return self.london_stations_df[self.london_stations_df['prolog_name'] == prolog_name]

    def get_line_color_for_prolog_name(self, name1, name2):
        station1 = self.parse_route_by_prolog_name(name1)
        station2 = self.parse_route_by_prolog_name(name2)
        connection = self.london_connections_df[(self.london_connections_df['station1'] == station1['id'].values[0]) & (
            self.london_connections_df['station2'] == station2['id'].values[0])]
        if len(connection) == 0:
            connection = self.london_connections_df[(self.london_connections_df['station1'] == station2['id'].values[0]) & (
                self.london_connections_df['station2'] == station1['id'].values[0])]
        line = self.london_lines_df[self.london_lines_df['line']
                                    == connection['line'].values[0]]
        color = "#"+line['colour'].values[0]
        return color
    
    def get_line_name_for_prolog_name(self, name1, name2):
        station1 = self.parse_route_by_prolog_name(name1)
        station2 = self.parse_route_by_prolog_name(name2)        
        connection = self.london_connections_df[(self.london_connections_df['station1'] == station1['id'].values[0]) & (
            self.london_connections_df['station2'] == station2['id'].values[0])]
        if len(connection) == 0:
            connection = self.london_connections_df[(self.london_connections_df['station1'] == station2['id'].values[0]) & (
                self.london_connections_df['station2'] == station1['id'].values[0])]
        line = self.london_lines_df[self.london_lines_df['line']
                                    == connection['line'].values[0]]
        return line['name'].values[0]

    def get_traces(self):
        lines = []
        for station1, station2, line, time in self.london_connections_df.values.tolist():
            station1_lat = self.london_stations_df[self.london_stations_df['id']
                                                   == station1]['latitude'].values[0]
            station1_long = self.london_stations_df[self.london_stations_df['id']
                                                    == station1]['longitude'].values[0]
            station2_lat = self.london_stations_df[self.london_stations_df['id']
                                                   == station2]['latitude'].values[0]
            station2_long = self.london_stations_df[self.london_stations_df['id']
                                                    == station2]['longitude'].values[0]
            name = self.london_lines_df[self.london_lines_df['line']
                                        == line]['name'].values[0]
            color = self.london_lines_df[self.london_lines_df['line']
                                         == line]['colour'].values[0]
            lines.append(go.Scattermapbox(
                mode="lines",
                lat=[station1_lat, station2_lat],
                lon=[station1_long, station2_long],
                line={'width': 4, 'color': "#"+color},
                name=name))
        return lines
    
    def filter_duplicate_traces(self, fig):
        names = set()
        fig.for_each_trace(lambda trace: trace.update(showlegend=False) if (trace.name in names) else names.add(trace.name))
        return fig

    def get_map_center(self):
        return self.london_stations_df['latitude'].mean(), self.london_stations_df['longitude'].mean()

    def get_default_map_layout(self, center_lat, center_lon):
        return go.Layout(
            mapbox_style="carto-positron",
            mapbox=dict(
                bearing=0,
                pitch=0,
                center=dict(lat=center_lat, lon=center_lon),
                zoom=11.8
            ))

    def get_markers(self):
        return go.Scattermapbox(
            lat=self.london_stations_df['latitude'].tolist(),
            lon=self.london_stations_df['longitude'].tolist(),
            text=self.london_stations_df['name'].tolist(),
            name="Stations",
            mode='markers+text',
            textposition="bottom center",
            marker=go.scattermapbox.Marker(size=10)
        )

    def filter_marker_and_traces(self, route):
        route_station = [self.parse_route_by_prolog_name(x) for x in route]
        lats = [x['latitude'].values[0] for x in route_station]
        longs = [x['longitude'].values[0] for x in route_station]
        names = [x['name'].values[0] for x in route_station]
        traces = [go.Scattermapbox(
            text=[names[i], names[i+1]],
            mode="markers+text+lines",
            lat=[lats[i], lats[i+1]],
            lon=[longs[i], longs[i+1]],
            line={'width': 4, 'color': self.get_line_color_for_prolog_name(
                route[i], route[i+1])},
            name=self.get_line_name_for_prolog_name(route[i], route[i+1]),
            marker=go.scattermapbox.Marker(size=10)
        ) for i in range(len(route_station)-1)]
        traces.append(go.Scattermapbox(
            mode="markers",
            lat=[lats[0], lats[-1]],
            lon=[longs[0], longs[-1]],
            marker=go.scattermapbox.Marker(
                size=[10,15], color=["blue", "red"]),
            name="Stations"
        ))
        center_lat = np.array(lats).mean()
        center_lon = np.array(longs).mean()
        output_text = " -> ".join(names)
        return traces, center_lat, center_lon, output_text
