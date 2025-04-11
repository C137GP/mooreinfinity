import dash
from dash import html, dcc, Output, Input, State
import pandas as pd
import io
import base64

# ✅ Register the page correctly with a nice menu label
dash.register_page(__name__, name="Inventory", path="/inventory")

layout = html.Div([
    html.H2("Inventory Completeness Testing"),
    html.H4("Upload Inventory Reports"),

    # Upload 1: Current Year Inventory
    html.Div([
        dcc.Upload(
            id='upload-inventory-1',
            children=html.Div(['Drag or Select CURRENT Year Inventory Report']),
            style={
                'width': '48%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        html.Div(id='inventory-name-1', style={"marginLeft": "10px", "color": "green"})
    ]),

    # Upload 2: Prior Year Inventory
    html.Div([
        dcc.Upload(
            id='upload-inventory-2',
            children=html.Div(['Drag or Select PRIOR Year Inventory Report']),
            style={
                'width': '48%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        html.Div(id='inventory-name-2', style={"marginLeft": "10px", "color": "green"})
    ]),

    # Upload 3: Movement Report
    html.Div([
        dcc.Upload(
            id='upload-inventory-3',
            children=html.Div(['Drag or Select MOVEMENT Report']),
            style={
                'width': '48%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        html.Div(id='inventory-name-3', style={"marginLeft": "10px", "color": "green"})
    ]),

    # Column mapping for each file
    html.Div(id="inventory-column-mapping-1"),
    html.Div(id="inventory-column-mapping-2"),
    html.Div(id="inventory-column-mapping-3"),

    # Download Button
    html.Button("Download Result", id="inventory-download-btn", n_clicks=0, disabled=True, style={"marginTop": "20px"}),

    dcc.Loading(
        id="inventory-loading-spinner",
        type="default",
        children=html.Div(id="inventory-download-status", style={"marginTop": "10px", "color": "#0074D9"})
    ),

    dcc.Download(id="inventory-download-excel")
])

# Callbacks
@dash.callback(Output('inventory-name-1', 'children'), Input('upload-inventory-1', 'filename'), prevent_initial_call=True)
def update_inventory_name1(name):
    return f"✅ Uploaded: {name}" if name else ""

@dash.callback(Output('inventory-name-2', 'children'), Input('upload-inventory-2', 'filename'), prevent_initial_call=True)
def update_inventory_name2(name):
    return f"✅ Uploaded: {name}" if name else ""

@dash.callback(Output('inventory-name-3', 'children'), Input('upload-inventory-3', 'filename'), prevent_initial_call=True)
def update_inventory_name3(name):
    return f"✅ Uploaded: {name}" if name else ""

@dash.callback(
    Output("inventory-download-btn", "disabled"),
    Input("upload-inventory-1", "contents"),
    Input("upload-inventory-2", "contents"),
    Input("upload-inventory-3", "contents"),
    prevent_initial_call=True
)
def toggle_download_button(file1, file2, file3):
    return not all([file1, file2, file3])

# Helpers for column detection
def parse_columns(contents):
    decoded = base64.b64decode(contents.split(',')[1])
    df = pd.read_excel(io.BytesIO(decoded), engine='openpyxl')
    return df.columns.tolist()

@dash.callback(Output("inventory-column-mapping-1", "children"), Input('upload-inventory-1', 'contents'), prevent_initial_call=True)
def show_mapping_1(contents):
    if contents:
        cols = parse_columns(contents)
        return html.Div([
            html.H5("Map Columns for Current Year Inventory"),
            dcc.Dropdown(id='item-code-dropdown-1', options=[{'label': c, 'value': c} for c in cols], placeholder="Select Item Code"),
            dcc.Dropdown(id='item-name-dropdown-1', options=[{'label': c, 'value': c} for c in cols], placeholder="Select Item Name"),
            dcc.Dropdown(id='quantity-dropdown-1', options=[{'label': c, 'value': c} for c in cols], placeholder="Select Quantity")
        ])

@dash.callback(Output("inventory-column-mapping-2", "children"), Input('upload-inventory-2', 'contents'), prevent_initial_call=True)
def show_mapping_2(contents):
    if contents:
        cols = parse_columns(contents)
        return html.Div([
            html.H5("Map Columns for Prior Year Inventory"),
            dcc.Dropdown(id='item-code-dropdown-2', options=[{'label': c, 'value': c} for c in cols], placeholder="Select Item Code"),
            dcc.Dropdown(id='item-name-dropdown-2', options=[{'label': c, 'value': c} for c in cols], placeholder="Select Item Name"),
            dcc.Dropdown(id='quantity-dropdown-2', options=[{'label': c, 'value': c} for c in cols], placeholder="Select Quantity")
        ])

@dash.callback(Output("inventory-column-mapping-3", "children"), Input('upload-inventory-3', 'contents'), prevent_initial_call=True)
def show_mapping_3(contents):
    if contents:
        cols = parse_columns(contents)
        return html.Div([
            html.H5("Map Columns for Movement Report"),
            dcc.Dropdown(id='item-code-dropdown-3', options=[{'label': c, 'value': c} for c in cols], placeholder="Select Item Code"),
            dcc.Dropdown(id='item-name-dropdown-3', options=[{'label': c, 'value': c} for c in cols], placeholder="Select Item Name"),
            dcc.Dropdown(id='quantity-dropdown-3', options=[{'label': c, 'value': c} for c in cols], placeholder="Select Quantity")
        ])

@dash.callback(
    Output("inventory-download-excel", "data"),
    Output("inventory-download-status", "children"),
    Input("inventory-download-btn", "n_clicks"),
    State("upload-inventory-1", "contents"),
    State("upload-inventory-2", "contents"),
    State("upload-inventory-3", "contents"),
    State('item-code-dropdown-1', 'value'),
    State('item-name-dropdown-1', 'value'),
    State('quantity-dropdown-1', 'value'),
    State('item-code-dropdown-2', 'value'),
    State('item-name-dropdown-2', 'value'),
    State('quantity-dropdown-2', 'value'),
    State('item-code-dropdown-3', 'value'),
    State('item-name-dropdown-3', 'value'),
    State('quantity-dropdown-3', 'value'),
    prevent_initial_call=True
)
def generate_inventory_excel(n_clicks, file1, file2, file3,
                             code1, name1, qty1,
                             code2, name2, qty2,
                             code3, name3, qty3):
    def parse(contents):
        return pd.read_excel(io.BytesIO(base64.b64decode(contents.split(',')[1])), engine='openpyxl')

    if not all([file1, file2, file3, code1, name1, qty1, code2, name2, qty2, code3, name3, qty3]):
        return None, "❌ Please upload all files and map all columns."

    try:
        df1 = parse(file1).rename(columns={code1: "ITEM CODE", name1: "ITEM NAME", qty1: "QUANTITY"})
        df2 = parse(file2).rename(columns={code2: "ITEM CODE", name2: "ITEM NAME", qty2: "QUANTITY"})
        df3 = parse(file3).rename(columns={code3: "ITEM CODE", name3: "ITEM NAME", qty3: "QUANTITY"})

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df1.to_excel(writer, index=False, sheet_name='Current Inventory')
            df2.to_excel(writer, index=False, sheet_name='Prior Inventory')
            df3.to_excel(writer, index=False, sheet_name='Movement Report')
        output.seek(0)
        return dcc.send_bytes(output.getvalue(), filename="inventory_result.xlsx"), "✅ Excel file ready for download."
    except Exception as e:
        return None, f"❌ Error: {str(e)}"
