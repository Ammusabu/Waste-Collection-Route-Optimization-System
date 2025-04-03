import folium
from folium.plugins import MarkerCluster
from ipywidgets import widgets
from IPython.display import display, HTML
import pandas as pd
import numpy as np
import networkx as nx
from geopy.distance import geodesic

# Generate bin data for each city
np.random.seed(42)
num_bins_per_city = 30
min_bins_for_route = 5

# City coordinates
cities = {
    'Ludhiana': (30.9010, 75.8573),
    'Amritsar': (31.6340, 74.8723),
    'Jalandhar': (31.3260, 75.5762),
    'Patiala': (30.3398, 76.3869),
    'Bathinda': (30.2070, 74.9455),
    'Mohali': (30.7046, 76.7179),
    'Firozpur': (30.9333, 74.6167),
    'Hoshiarpur': (31.5320, 75.9172),
    'Moga': (30.8154, 75.1688),
    'Pathankot': (32.2736, 75.6522)
}

# Generate bins data
data = []
for city, (lat, lon) in cities.items():
    for i in range(num_bins_per_city):
        bin_lat = lat + np.random.normal(0, 0.02)
        bin_lon = lon + np.random.normal(0, 0.02)
        bin_type = np.random.choice(['General', 'Recyclable', 'Hazardous'])
        capacity = np.random.randint(50, 200)
        current_fill = min(capacity, np.random.randint(0, capacity + 20))
        fill_percentage = (current_fill / capacity) * 100

        if fill_percentage > 90:
            urgency = 'Critical'
        elif fill_percentage > 70:
            urgency = 'High'
        elif fill_percentage > 40:
            urgency = 'Medium'
        else:
            urgency = 'Low'

        data.append({
            'city': city,
            'bin_id': f"{city[:3]}-{i+1}",
            'latitude': bin_lat,
            'longitude': bin_lon,
            'type': bin_type,
            'capacity': capacity,
            'current_fill': current_fill,
            'fill_percentage': fill_percentage,
            'urgency': urgency,
            'last_collected': 'N/A'
        })

bins_df = pd.DataFrame(data)

# Add depots
depots = []
for city, (lat, lon) in cities.items():
    depots.append({
        'city': city,
        'bin_id': f"{city[:3]}-DEPOT",
        'latitude': lat,
        'longitude': lon,
        'type': 'Depot',
        'capacity': 1000,
        'current_fill': 0,
        'fill_percentage': 0,
        'urgency': 'None',
        'last_collected': 'N/A'
    })

depots_df = pd.DataFrame(depots)
full_df = pd.concat([bins_df, depots_df], ignore_index=True)

def calculate_distance_matrix(locations):
    n = len(locations)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                coord1 = (locations[i]['latitude'], locations[i]['longitude'])
                coord2 = (locations[j]['latitude'], locations[j]['longitude'])
                dist_matrix[i][j] = geodesic(coord1, coord2).km
    return dist_matrix

def find_optimal_route(locations, depot_index=0):
    if len(locations) < 3:
        return [0, 1, 0] if len(locations) == 2 else [0]

    G = nx.Graph()
    dist_matrix = calculate_distance_matrix(locations)

    for i in range(len(locations)):
        for j in range(i+1, len(locations)):
            urgency_factor = 1
            if locations[i]['urgency'] == 'Critical':
                urgency_factor = 0.5
            elif locations[i]['urgency'] == 'High':
                urgency_factor = 0.7
            elif locations[i]['urgency'] == 'Medium':
                urgency_factor = 0.9

            if locations[j]['urgency'] == 'Critical':
                urgency_factor *= 0.5
            elif locations[j]['urgency'] == 'High':
                urgency_factor *= 0.7
            elif locations[j]['urgency'] == 'Medium':
                urgency_factor *= 0.9

            G.add_edge(i, j, weight=dist_matrix[i][j] * urgency_factor)

    tsp_route = nx.approximation.traveling_salesman_problem(G, cycle=True)

    if depot_index in tsp_route:
        idx = tsp_route.index(depot_index)
        tsp_route = tsp_route[idx:] + tsp_route[:idx]
        if tsp_route[-1] != depot_index:
            tsp_route.append(depot_index)
    else:
        tsp_route = [depot_index] + tsp_route + [depot_index]

    optimized_route = [tsp_route[0]]
    for node in tsp_route[1:]:
        if node != optimized_route[-1]:
            optimized_route.append(node)

    return optimized_route

def show_city_route(city_name, selected_bin_types=['General', 'Recyclable', 'Hazardous'], min_fill=50):
    city_bins = full_df[(full_df['city'] == city_name) &
                       (full_df['type'].isin(selected_bin_types)) &
                       (full_df['fill_percentage'] >= min_fill)].copy()

    if len(city_bins) < min_bins_for_route:
        display(HTML(f"""
        <div style="background:#fff3cd; padding:10px; margin-bottom:10px; border-radius:5px">
            <h3 style="margin-top:0; color:#856404">Not enough bins for route optimization</h3>
            <p>Only {len(city_bins)} bins match your criteria (minimum {min_bins_for_route} needed).</p>
            <p>Try adjusting the filters to include more bins.</p>
        </div>
        """))
        return

    depot = full_df[(full_df['city'] == city_name) & (full_df['type'] == 'Depot')].iloc[0]
    locations = [depot.to_dict()] + city_bins.to_dict('records')
    route_indices = find_optimal_route(locations)
    optimized_route = [locations[i] for i in route_indices]

    total_distance = 0
    for i in range(len(optimized_route)-1):
        coord1 = (optimized_route[i]['latitude'], optimized_route[i]['longitude'])
        coord2 = (optimized_route[i+1]['latitude'], optimized_route[i+1]['longitude'])
        total_distance += geodesic(coord1, coord2).km

    m = folium.Map(
        location=cities[city_name],
        zoom_start=13,
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google Maps'
    )

    # Add depot
    folium.Marker(
        location=[depot['latitude'], depot['longitude']],
        popup=f"<b>Depot</b><br>Collection Center",
        icon=folium.Icon(color='black', icon='industry', prefix='fa')
    ).add_to(m)

    # Add route
    route_coords = [(loc['latitude'], loc['longitude']) for loc in optimized_route]
    folium.PolyLine(
        route_coords,
        color='blue',
        weight=3,
        opacity=0.8,
        popup=f"Optimized Route: {total_distance:.2f} km"
    ).add_to(m)

    # Add bins
    for loc in optimized_route[1:-1]:
        if loc['urgency'] == 'Critical':
            icon_color = 'red'
        elif loc['urgency'] == 'High':
            icon_color = 'orange'
        elif loc['urgency'] == 'Medium':
            icon_color = 'lightblue'
        else:
            icon_color = 'green'

        popup_text = f"""
        <b>Bin {loc['bin_id']}</b><br>
        Type: {loc['type']}<br>
        Fill: {loc['current_fill']}/{loc['capacity']}L ({loc['fill_percentage']:.1f}%)<br>
        Urgency: {loc['urgency']}
        """

        folium.Marker(
            location=[loc['latitude'], loc['longitude']],
            popup=folium.Popup(popup_text, max_width=250),
            icon=folium.Icon(color=icon_color, icon='trash' if loc['type'] != 'Hazardous' else 'warning-sign', prefix='glyphicon')
        ).add_to(m)

    display(HTML(f"""
    <div style="background:#f0f0f0; padding:10px; margin-bottom:10px; border-radius:5px">
        <h3 style="margin-top:0">{city_name} Waste Collection Route</h3>
        <p><b>Route Distance:</b> {total_distance:.2f} km</p>
        <p><b>Bins Collected:</b> {len(optimized_route)-2}</p>
        <p><b>Critical Bins:</b> {len([b for b in optimized_route if b.get('urgency') == 'Critical'])}</p>
        <p><b>High Urgency Bins:</b> {len([b for b in optimized_route if b.get('urgency') == 'High'])}</p>
    </div>
    """))

    display(m)

# Create UI controls
city_dropdown = widgets.Dropdown(
    options=list(cities.keys()),
    value='Ludhiana',
    description='Select City:',
    disabled=False
)

bin_type_selector = widgets.SelectMultiple(
    options=['General', 'Recyclable', 'Hazardous'],
    value=['General', 'Recyclable', 'Hazardous'],
    description='Bin Types:',
    disabled=False
)

fill_threshold_slider = widgets.IntSlider(
    value=50,
    min=0,
    max=100,
    step=5,
    description='Min Fill %:',
    disabled=False
)

optimize_button = widgets.Button(
    description="Show Optimized Route",
    button_style='success'
)

def on_optimize_click(b):
    display(HTML(''))
    show_city_route(
        city_name=city_dropdown.value,
        selected_bin_types=list(bin_type_selector.value),
        min_fill=fill_threshold_slider.value
    )

optimize_button.on_click(on_optimize_click)

# Display UI
display(HTML("""
<style>
.control-panel {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 5px;
    margin-bottom: 15px;
    border: 1px solid #dee2e6;
}
.control-title {
    font-weight: bold;
    margin-bottom: 10px;
    color: #495057;
}
</style>
"""))

display(HTML("<h2 style='text-align:center'>Punjab Waste Collection Route Optimizer</h2>"))
display(HTML("<div class='control-panel'><div class='control-title'>Route Parameters</div>"))
display(city_dropdown)
display(bin_type_selector)
display(fill_threshold_slider)
display(optimize_button)
display(HTML("</div>"))

# Initial display
show_city_route('Amritsar')
