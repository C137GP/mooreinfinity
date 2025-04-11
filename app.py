from dash import Dash, html, dcc
import dash

# Initialize Dash app with multi-page support and callback exception suppression
app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True
)
server = app.server

# App layout
app.layout = html.Div([

    # Header with logo and navigation
    html.Div([
        # Logo (on the left)
        html.Img(src="/assets/moore-logo.svg", className="logo"),
        html.Link(rel='icon', href='/assets/moore-logo.ico', type='image/x-icon'),

        # Page links (on the right)
        html.Div([
            dcc.Link(
                f"{page['name']}",
                href=page["relative_path"],
                className='menu-item'
            )
            for page in dash.page_registry.values()
        ], className='menu'),
    ], className="header"),

    html.Hr(),

    # Page content will be rendered here
    dash.page_container,

    # Footer
    html.Div([
        html.Hr(),
        html.H4("Support:"),
        html.H5("Address:"),
        html.H5("Silver Stream Business Park, 10 Muswell Road, Bryanston, Sandton, 2191"),
        html.H5("Email:"),
        html.H5("Harrys@mooreinfinity.com"),
    ], className="footer")
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
