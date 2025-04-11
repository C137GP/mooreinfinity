import dash
from dash import html

# Register as the home page (root URL "/")
dash.register_page(__name__, path="/", name="Home")

# Page layout
layout = html.Div([
    html.H1("Welcome to Moore Infinity", style={"textAlign": "center"}),
    html.P("This is your dashboard home. Use the navigation above to access reports and tools.",
           style={"textAlign": "center", "fontSize": "18px", "marginTop": "20px"}),

    html.Div([
        html.H3("Available Modules:"),
        html.Ul([
            html.Li("🧾 TB vs TB Testing"),
            html.Li("📦 Inventory Reporting"),
            html.Li("📊 GL Only Exporting"),
            html.Li("🛠️ Column Mapping & Validation"),
        ])
    ], style={"margin": "40px"})
])
