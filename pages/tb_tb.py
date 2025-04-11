import dash
from dash import html, dcc, Output, Input, State
import pandas as pd
import io
import base64

# Register the page
dash.register_page(__name__, path='/tb-tb', name="TB vs TB")

# Layout
layout = html.Div([
    html.H2("TB-TB Testing"),
    html.H4("Upload Trial Balances and General Ledger"),

    # Upload 1: Current Year TB
    html.Div([
        dcc.Upload(
            id='upload-file-1',
            children=html.Div(['Drag or Select CURRENT Year Trial Balance']),
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
        html.Div(id='file-name-1', style={"marginLeft": "10px", "color": "green"})
    ]),

    # Upload 2: Prior Year TB
    html.Div([
        dcc.Upload(
            id='upload-file-2',
            children=html.Div(['Drag or Select PRIOR Year Trial Balance']),
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
        html.Div(id='file-name-2', style={"marginLeft": "10px", "color": "green"})
    ]),

    # Upload 3: General Ledger
    html.Div([
        dcc.Upload(
            id='upload-file-3',
            children=html.Div(['Drag or Select GENERAL LEDGER']),
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
        html.Div(id='file-name-3', style={"marginLeft": "10px", "color": "green"})
    ]),

    # Column Mapping UI (Visible after file uploads)
    html.Div(id="column-mapping-1"),
    html.Div(id="column-mapping-2"),
    html.Div(id="column-mapping-3"),

    html.Button("Download Result", id="download-btn", n_clicks=0, disabled=True, style={"marginTop": "20px"}),

    # Loading spinner and status message
    dcc.Loading(
        id="loading-spinner",
        type="default",  # Show default spinner
        children=html.Div(id="download-status", style={"marginTop": "10px", "color": "#0074D9"})
    ),

    dcc.Download(id="download-excel")
])

# Display filenames after upload
@dash.callback(
    Output('file-name-1', 'children'),
    Input('upload-file-1', 'filename'),
    prevent_initial_call=True
)
def update_filename1(name):
    return f"✅ Uploaded: {name}" if name else ""

@dash.callback(
    Output('file-name-2', 'children'),
    Input('upload-file-2', 'filename'),
    prevent_initial_call=True
)
def update_filename2(name):
    return f"✅ Uploaded: {name}" if name else ""

@dash.callback(
    Output('file-name-3', 'children'),
    Input('upload-file-3', 'filename'),
    prevent_initial_call=True
)
def update_filename3(name):
    return f"✅ Uploaded: {name}" if name else ""

# Enable download button only when all files are uploaded
@dash.callback(
    Output("download-btn", "disabled"),
    Input("upload-file-1", "contents"),
    Input("upload-file-2", "contents"),
    Input("upload-file-3", "contents"),
    prevent_initial_call=True
)
def toggle_download_button(file1, file2, file3):
    return not all([file1, file2, file3])

# Display column mappings for each file after upload
@dash.callback(
    Output("column-mapping-1", "children"),
    Input('upload-file-1', 'contents'),
    prevent_initial_call=True
)
def display_column_mapping_1(contents):
    if contents is None:
        return ""
    df = pd.read_excel(io.BytesIO(base64.b64decode(contents.split(',')[1])), engine='openpyxl')
    columns = df.columns.tolist()
    return html.Div([
        html.H5("Map Columns for Current Year Trial Balance"),
        dcc.Dropdown(id='account-code-dropdown-1', options=[{'label': col, 'value': col} for col in columns], placeholder="Select Account Code"),
        dcc.Dropdown(id='account-name-dropdown-1', options=[{'label': col, 'value': col} for col in columns], placeholder="Select Account Name"),
        dcc.Dropdown(id='amount-dropdown-1', options=[{'label': col, 'value': col} for col in columns], placeholder="Select Amount")
    ])

@dash.callback(
    Output("column-mapping-2", "children"),
    Input('upload-file-2', 'contents'),
    prevent_initial_call=True
)
def display_column_mapping_2(contents):
    if contents is None:
        return ""
    df = pd.read_excel(io.BytesIO(base64.b64decode(contents.split(',')[1])), engine='openpyxl')
    columns = df.columns.tolist()
    return html.Div([
        html.H5("Map Columns for Prior Year Trial Balance"),
        dcc.Dropdown(id='account-code-dropdown-2', options=[{'label': col, 'value': col} for col in columns], placeholder="Select Account Code"),
        dcc.Dropdown(id='account-name-dropdown-2', options=[{'label': col, 'value': col} for col in columns], placeholder="Select Account Name"),
        dcc.Dropdown(id='amount-dropdown-2', options=[{'label': col, 'value': col} for col in columns], placeholder="Select Amount")
    ])

@dash.callback(
    Output("column-mapping-3", "children"),
    Input('upload-file-3', 'contents'),
    prevent_initial_call=True
)
def display_column_mapping_3(contents):
    if contents is None:
        return ""
    df = pd.read_excel(io.BytesIO(base64.b64decode(contents.split(',')[1])), engine='openpyxl')
    columns = df.columns.tolist()
    return html.Div([
        html.H5("Map Columns for General Ledger"),
        dcc.Dropdown(id='account-code-dropdown-3', options=[{'label': col, 'value': col} for col in columns], placeholder="Select Account Code"),
        dcc.Dropdown(id='account-name-dropdown-3', options=[{'label': col, 'value': col} for col in columns], placeholder="Select Account Name"),
        dcc.Dropdown(id='amount-dropdown-3', options=[{'label': col, 'value': col} for col in columns], placeholder="Select Amount")
    ])

# Generate download file and show status
@dash.callback(
    Output("download-excel", "data"),
    Output("download-status", "children"),
    Input("download-btn", "n_clicks"),
    State("upload-file-1", "contents"),
    State("upload-file-2", "contents"),
    State("upload-file-3", "contents"),
    State('account-code-dropdown-1', 'value'),
    State('account-name-dropdown-1', 'value'),
    State('amount-dropdown-1', 'value'),
    State('account-code-dropdown-2', 'value'),
    State('account-name-dropdown-2', 'value'),
    State('amount-dropdown-2', 'value'),
    State('account-code-dropdown-3', 'value'),
    State('account-name-dropdown-3', 'value'),
    State('amount-dropdown-3', 'value'),
    prevent_initial_call=True
)
def generate_excel(n_clicks, curr_tb_content, prior_tb_content, gl_content,
                   curr_account_code, curr_account_name, curr_amount,
                   prior_account_code, prior_account_name, prior_amount,
                   gl_account_code, gl_account_name, gl_amount):

    def parse_contents(contents):
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        return pd.read_excel(io.BytesIO(decoded), engine="openpyxl")

    # Ensure all files and mappings are provided
    if not all([curr_tb_content, prior_tb_content, gl_content,
                curr_account_code, curr_account_name, curr_amount,
                prior_account_code, prior_account_name, prior_amount,
                gl_account_code, gl_account_name, gl_amount]):
        return None, "❌ Please upload all files and map columns before downloading."

    try:
        curr_tb = parse_contents(curr_tb_content)
        prior_tb = parse_contents(prior_tb_content)
        gl = parse_contents(gl_content)

        # Apply mappings
        curr_tb = curr_tb.rename(columns={curr_account_code: "ACCOUNT CODE",
                                          curr_account_name: "ACCOUNT NAME",
                                          curr_amount: "AMOUNT"})

        prior_tb = prior_tb.rename(columns={prior_account_code: "ACCOUNT CODE",
                                            prior_account_name: "ACCOUNT NAME",
                                            prior_amount: "AMOUNT"})

        gl = gl.rename(columns={gl_account_code: "ACCOUNT CODE",
                                gl_account_name: "ACCOUNT NAME",
                                gl_amount: "AMOUNT"})

        # Output to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            curr_tb.to_excel(writer, index=False, sheet_name='Current TB')
            prior_tb.to_excel(writer, index=False, sheet_name='Prior TB')
            gl.to_excel(writer, index=False, sheet_name='General Ledger')
        output.seek(0)

        return dcc.send_bytes(output.getvalue(), filename="result.xlsx"), "✅ Excel file ready for download."

    except Exception as e:
        return None, f"❌ Error: {str(e)}"
