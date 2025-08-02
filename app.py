import dash
from dash import html, dcc, Input, Output
import dash_table
import pandas as pd
import plotly.express as px
import sqlite3

# Connect to SQLite and read data
conn = sqlite3.connect('sales.db')
df = pd.read_sql_query("SELECT * FROM sales", conn)
conn.close()

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "SQL Sales Dashboard"

# App layout
app.layout = html.Div(children=[
    html.H1("SQL Sales Dashboard"),

    html.Label("Filter by Region:"),
    dcc.Dropdown(
        id='region-filter',
        options=[{'label': r, 'value': r} for r in df['region'].unique()],
        value=None,
        placeholder="Select a region"
    ),

    html.Label("Filter by Product:"),
    dcc.Dropdown(
        id='product-filter',
        options=[{'label': p, 'value': p} for p in df['product'].unique()],
        value=None,
        placeholder="Select a product"
    ),

    html.Br(),
    html.H2("Summary Table"),
    dash_table.DataTable(
        id='summary-table',
        columns=[
            {"name": "region", "id": "region"},
            {"name": "total_sales", "id": "total_sales"},
            {"name": "total_transactions", "id": "total_transactions"}
        ],
        data=[],  # Will be filled by callback
        style_table={'width': '60%', 'margin': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={'backgroundColor': '#f2f2f2', 'fontWeight': 'bold'}
    ),

    html.Br(),
    dcc.Graph(id='bar-chart')
])

# Callback to update chart and summary table
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('summary-table', 'data')],
    [Input('region-filter', 'value'),
     Input('product-filter', 'value')]
)
def update_dashboard(selected_region, selected_product):
    filtered_df = df.copy()

    if selected_region:
        filtered_df = filtered_df[filtered_df['region'] == selected_region]

    if selected_product:
        filtered_df = filtered_df[filtered_df['product'] == selected_product]

    # Update chart
    fig = px.bar(
        filtered_df,
        x='product',
        y='price',
        color='product',
        title="Sales by Product" +
              (f" in {selected_region}" if selected_region else "") +
              (f" - {selected_product}" if selected_product else "")
    )

    # Update summary table
    if not filtered_df.empty:
        summary_df = filtered_df.groupby('region').agg(
            total_sales=('price', 'sum'),
            total_transactions=('id', 'count')
        ).reset_index()
        table_data = summary_df.to_dict('records')
    else:
        table_data = []

    return fig, table_data

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
