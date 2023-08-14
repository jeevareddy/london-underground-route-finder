import numpy as np
import gradio as gr
from src.utils import Utils
from swiplserver import PrologMQI
import plotly.graph_objects as go

facts_path = "./src/facts.pl"
search_algorithm_path = "./src/search_algorithms.pl"

utils = Utils()
possible_routes = []

def query(origin, destination):
    with PrologMQI() as mqi:
        with mqi.create_thread() as prolog_thread:
            result = prolog_thread.query(f'consult("{facts_path}").')
            print(f"Loaded facts: {result}")
            result = prolog_thread.query(f'consult("{search_algorithm_path}").')
            print(f"Loaded rules: {result}")
            print(f"Query Path: {origin} - - to - - {destination}")
            prolog_thread.query_async(f"a_star_search({utils.remove_spl_chars(origin)}, {utils.remove_spl_chars(destination)}, Path).", find_all=False)
            result = prolog_thread.query_async_result()
            if (result == False) or (len(result) == 0):
                return []
            print(f"Total Results: {len(result)}")
            routes = result[0]['Path']
            print(f"Result route: {routes}")
            return routes

def load_map():
    center_lat, center_lon = utils.get_map_center()
    fig = go.Figure(layout=utils.get_default_map_layout(center_lat, center_lon))
    fig.add_traces(utils.get_traces())
    fig.add_trace(utils.get_markers())
    fig = utils.filter_duplicate_traces(fig)
    return fig

def filter_map(origin, destination):
    center_lat, center_lon = utils.get_map_center()
    output_text = ""    
    traces = []
    if (len(origin) > 0) and (len(destination) > 0):
        route = query(origin, destination)
        if len(route) == 0:
            output_text = "No Route Found"
        else:
            traces, center_lat, center_lon, output_text = utils.filter_marker_and_traces(route)
    else:
        traces = utils.get_traces()

    fig = go.Figure(data=traces,layout=utils.get_default_map_layout(center_lat, center_lon))
    fig = utils.filter_duplicate_traces(fig)
    return fig, output_text

with gr.Blocks() as demo:
    with gr.Column():
        gr.Label(value="London Underground Stations Route Finder", label="")
        map = gr.Plot(label="London Underground Station Map")
        with gr.Row():
            origin = gr.Dropdown(
                choices=utils.get_all_station_names(), label="Origin 🔵")
            destination = gr.Dropdown(
                choices=utils.get_all_station_names(), label="Destination 🔴")
        with gr.Row():
            btn_clear = gr.Button(value="Clear")
            btn_search = gr.Button(value="Search")
            btn_clear.click(load_map, [], map)
        output_label = gr.Label(label="Optimal Route")
        btn_search.click(filter_map, [origin, destination], [map, output_label])
    demo.load(load_map, [], map)

demo.launch()
