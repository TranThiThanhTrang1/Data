# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into a pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create options for the dropdown
launch_sites = spacex_df['Launch Site'].unique()
options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=options,
        value='ALL',  # Default value
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # Pie chart for successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # Range Slider for Payload selection
    dcc.RangeSlider(
        id='payload-slider',
        min=0,  # Starting point of the slider
        max=10000,  # Ending point of the slider
        step=1000,  # Interval on the slider
        value=[min_payload, max_payload],  # Current selected range
        marks={i: str(i) for i in range(0, 10001, 2000)}  # Marks on the slider
    ),

    # Scatter chart for payload vs. launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(selected_site):
    # Filter the DataFrame based on the selected site
    if selected_site == 'ALL':
        # Use all data for all sites
        success_counts = spacex_df['class'].value_counts()
        fig = px.pie(
            names=success_counts.index.map({0: 'Failed', 1: 'Successful'}),
            values=success_counts.values,
            title='Total Launch Success Counts for All Sites'
        )
    else:
        # Filter for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = filtered_df['class'].value_counts()
        
        fig = px.pie(
            names=success_counts.index.map({0: 'Failed', 1: 'Successful'}),
            values=success_counts.values,
            title=f'Launch Success Counts for {selected_site}'
        )
    
    return fig

# Callback for the scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df
    
    # Filter by selected site
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Filter by payload range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) &
                               (filtered_df['Payload Mass (kg)'] <= payload_range[1])]
    
    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',  # Color by booster version
        title='Payload vs. Launch Success',
        labels={'class': 'Success (1) / Failure (0)'},
        hover_data=['Booster Version Category']  # Show booster version on hover
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)  # Enable debug mode for better error messages