import dash
from dash import html, dcc, Output, Input, State, callback_context, dash_table
import pandas as pd
import io
import base64
import difflib

dash.register_page(__name__, path="/gl_mapping", name="GL Mapping")

stored_data = {"gl_df": None, "lead_column": None}

layout = html.Div([
    html.H2("Upload General Ledger and Map Columns"),

    html.Div([
        dcc.Upload(
            id='upload-gl',
            children=html.Div(['Drag or Select General Ledger']),
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
        html.Div(id='gl-file-name', style={"marginLeft": "10px", "color": "green"})
    ]),

    html.Div(id="column-mapping", style={"marginTop": "20px"}),
    html.Div(id="trace-options", style={"marginTop": "20px"}),

    html.Button("Download Trace Excel", id="gl-download-btn", n_clicks=0, style={"marginTop": "20px"}, disabled=True),

    dcc.Loading(
        id="gl-loading-spinner",
        type="default",
        children=html.Div(id="gl-download-status", style={"marginTop": "10px", "color": "#0074D9"})
    ),

    dcc.Download(id="gl-download-excel"),

    html.Div(id="trace-preview", style={"marginTop": "40px"})
])


@dash.callback(
    Output('gl-file-name', 'children', allow_duplicate=True),
    Input('upload-gl', 'filename'),
    prevent_initial_call=True
)
def update_gl_filename(name):
    return f"✅ Uploaded: {name}" if name else ""


@dash.callback(
    Output('column-mapping', 'children'),
    Output("gl-download-btn", "disabled"),
    Input('upload-gl', 'contents'),
    prevent_initial_call=True
)
def generate_column_mapping(gl_content):
    def parse_contents(contents):
        _, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        return pd.read_excel(io.BytesIO(decoded), engine="openpyxl")

    try:
        gl_df = parse_contents(gl_content)
        stored_data["gl_df"] = gl_df
        detected_columns = gl_df.columns.tolist()

        required_columns = [
            "ACCOUNT CODE", "ACCOUNT NAME", "TRANSACTION DATE", "TRANSACTION SOURCE",
            "LEAD SHEET NUMBER", "AMOUNT", "TRANSACTION NUMBER", "DOCUMENT NUMBER"
        ]

        dropdowns = []
        for col in required_columns:
            closest_match = difflib.get_close_matches(col, detected_columns, n=1, cutoff=0.5)
            preselected = closest_match[0] if closest_match else None
            dropdowns.append(html.Div([
                html.Label(f"Select column for: {col}"),
                dcc.Dropdown(
                    id=f"dropdown-{col}",
                    options=[{'label': c, 'value': c} for c in detected_columns],
                    placeholder=f"Select {col}",
                    value=preselected,
                    style={"width": "50%"}
                )
            ], style={"marginBottom": "20px"}))

        return dropdowns, False

    except Exception as e:
        return html.Div([f"❌ Error: {str(e)}"]), True


@dash.callback(
    Output("trace-options", "children"),
    Input("dropdown-LEAD SHEET NUMBER", "value"),
    prevent_initial_call=True
)
def show_trace_dropdowns(lead_col):
    if not lead_col or stored_data["gl_df"] is None:
        return ""

    try:
        stored_data["lead_column"] = lead_col
        unique_leads = stored_data["gl_df"][lead_col].dropna().unique()
        options = [{"label": str(val), "value": str(val)} for val in sorted(unique_leads)]

        return html.Div([
            html.H5("Trace Between Lead Sheets"),
            html.Div([
                html.Label("Lead to trace FROM:"),
                dcc.Dropdown(id="lead-from", options=options, placeholder="Select origin lead")
            ], style={"marginBottom": "10px", "width": "50%"}),

            html.Div([
                html.Label("Lead to trace TO:"),
                dcc.Dropdown(id="lead-to", options=options, placeholder="Select destination lead")
            ], style={"marginBottom": "10px", "width": "50%"})
        ])

    except Exception as e:
        return html.Div([f"❌ Error generating trace options: {str(e)}"])


def trace_transactions_between_leads(df, lead_from, lead_to):
    lead_to = int(lead_to)
    lead_from = int(lead_from)
    df = df.copy()
    required = [
        "ACCOUNT CODE", "ACCOUNT NAME", "TRANSACTION DATE", "TRANSACTION SOURCE",
        "LEAD SHEET NUMBER", "AMOUNT", "TRANSACTION NUMBER", "DOCUMENT NUMBER"
    ]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    df_from = df[df["LEAD SHEET NUMBER"] == lead_from]
    df_to = df[df["LEAD SHEET NUMBER"] == lead_to]

    pivot_from = df_from.groupby("TRANSACTION NUMBER").agg({
        "DOCUMENT NUMBER": "count",
        "AMOUNT": "sum"
    })

    pivot_to = df_to.groupby("TRANSACTION NUMBER").agg({
        "DOCUMENT NUMBER": "count",
        "AMOUNT": "sum"
    })

    matched_amounts = []
    matched_counts = []
    for txn in pivot_from.index:
        if txn in pivot_to.index:
            matched_amounts.append(pivot_to.loc[txn, "AMOUNT"])
            matched_counts.append(pivot_to.loc[txn, "DOCUMENT NUMBER"])
        else:
            matched_amounts.append(0)
            matched_counts.append(0)

    pivot_from[f'AMOUNT_CL_SUM_{lead_to}'] = matched_amounts
    pivot_from[f'NO_OF_RECS_{lead_to}'] = matched_counts
    pivot_from['DIFFERENCE'] = pivot_from["AMOUNT"] + pivot_from[f'AMOUNT_CL_SUM_{lead_to}']

    not_found = pivot_from[pivot_from[f'NO_OF_RECS_{lead_to}'] == 0]
    not_found_txns = not_found.index
    not_found_frame = df[df["TRANSACTION NUMBER"].isin(not_found_txns)]
    not_found_frame = not_found_frame[df["LEAD SHEET NUMBER"] != lead_from]

    summary = not_found_frame.groupby(["LEAD SHEET NUMBER", "ACCOUNT NAME"]).agg(
        NUMBER_OF_RECORDS=("AMOUNT", "count"),
        AMOUNT=("AMOUNT", "sum")
    ).reset_index()

    return pivot_from.reset_index(), summary


@dash.callback(
    Output("gl-download-excel", "data", allow_duplicate=True),
    Output("gl-download-status", "children", allow_duplicate=True),
    Input("gl-download-btn", "n_clicks"),
    State("upload-gl", "contents"),
    State("dropdown-ACCOUNT CODE", "value"),
    State("dropdown-ACCOUNT NAME", "value"),
    State("dropdown-TRANSACTION DATE", "value"),
    State("dropdown-TRANSACTION SOURCE", "value"),
    State("dropdown-LEAD SHEET NUMBER", "value"),
    State("dropdown-AMOUNT", "value"),
    State("dropdown-TRANSACTION NUMBER", "value"),
    State("dropdown-DOCUMENT NUMBER", "value"),
    State("lead-from", "value"),
    State("lead-to", "value"),
    prevent_initial_call=True
)
def generate_gl_excel(n_clicks, gl_content, *cols):
    if not callback_context.triggered:
        return dash.no_update, dash.no_update

    (
        acc_code, acc_name, txn_date, txn_source,
        lead, amt, txn_num, doc_num, from_lead, to_lead
    ) = cols

    def parse(contents):
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        return pd.read_excel(io.BytesIO(decoded), engine="openpyxl")

    try:
        df = parse(gl_content)

        # Map the selected dropdown values to standard column names
        mapping = {
            acc_code: "ACCOUNT CODE",
            acc_name: "ACCOUNT NAME",
            txn_date: "TRANSACTION DATE",
            txn_source: "TRANSACTION SOURCE",
            lead: "LEAD SHEET NUMBER",
            amt: "AMOUNT",
            txn_num: "TRANSACTION NUMBER",
            doc_num: "DOCUMENT NUMBER"
        }

        # Remove entries with None as keys (unselected dropdowns)
        clean_mapping = {k: v for k, v in mapping.items() if k is not None}

        # DEBUG: Print mapping info and original columns
        print("Original columns:", df.columns.tolist())
        print("User-selected mapping:", mapping)
        print("Cleaned mapping used for renaming:", clean_mapping)

        # Rename using the cleaned mapping
        df = df.rename(columns=clean_mapping)

        # DEBUG: Print columns after renaming
        print("Columns after renaming:", df.columns.tolist())

        required_cols = list(mapping.values())

        # Check that all required columns exist
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"❌ Missing columns after renaming: {missing}")

        # Select only the required columns
        df = df[required_cols]

        # Run trace logic
        exist_found, exist_nf = trace_transactions_between_leads(df, from_lead, to_lead)
        comp_found, comp_nf = trace_transactions_between_leads(df, to_lead, from_lead)

        # Write to Excel in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            exist_found.to_excel(writer, index=False, sheet_name="Existence-Found")
            exist_nf.to_excel(writer, index=False, sheet_name="Existence-Not-Found")
            comp_found.to_excel(writer, index=False, sheet_name="Completeness-Found")
            comp_nf.to_excel(writer, index=False, sheet_name="Completeness-NoTFound")

        output.seek(0)
        return dcc.send_bytes(output.read(), filename="trace_results.xlsx"), "✅ Trace Excel ready for download."

    except Exception as e:
        print("Error during processing:", str(e))  # Debug log
        return None, f"❌ Error: {str(e)}"
