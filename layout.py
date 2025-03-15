def create_layout(fig_map, fig_pm25, fig_humidity, fig_temperature, prediction_areas):
    """
    Create the main layout for the Dash application
    
    Parameters:
    -----------
    fig_map : plotly.graph_objects.Figure
        The map figure with prediction areas
    fig_pm25, fig_humidity, fig_temperature : plotly.graph_objects.Figure
        The time series figures for each metric
    prediction_areas : list
        List of prediction areas data
        
    Returns:
    --------
    dash_bootstrap_components.Container
        The main container with the dashboard layout
    """
    
    # คำนวณค่าเฉลี่ยของข้อมูล
    avg_pm25 = data['PM 2.5']['df'][data['PM 2.5']['col']].mean()
    avg_humidity = data['Humidity']['df'][data['Humidity']['col']].mean()
    avg_temperature = data['Temperature']['df'][data['Temperature']['col']].mean()

    return dbc.Container([
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H2("Dashboard การพยากรณ์", className="text-white"),
                    html.P("ข้อมูลพยากรณ์ PM 2.5, ความชื้น และ อุณหภูมิ (7 วัน)", className="text-white"),
                    
                    # ส่วนแสดงค่าเฉลี่ย (ปรับรูปแบบให้คล้ายภาพ)
                    html.Div([
                        html.H4("ค่าเฉลี่ยรายวัน", className="text-white mb-3 text-center"),
                        dbc.Row([ 
                            dbc.Col(
                                html.Div([
                                    html.P("PM 2.5", className="text-white mb-1 text-center"),
                                    html.P(f"{avg_pm25:.2f} μg/m³", className="text-white h1 text-center")
                                ], className="p-3 rounded bg-secondary shadow"), width=4
                            ),
                            dbc.Col(
                                html.Div([
                                    html.P("ความชื้น", className="text-white mb-1 text-center"),
                                    html.P(f"{avg_humidity:.2f}%", className="text-white h1 text-center")
                                ], className="p-3 rounded bg-secondary shadow"), width=4
                            ),
                            dbc.Col(
                                html.Div([
                                    html.P("อุณหภูมิ", className="text-white mb-1 text-center"),
                                    html.P(f"{avg_temperature:.2f}°C", className="text-white h1 text-center")
                                ], className="p-3 rounded bg-secondary shadow"), width=4
                            ),
                        ])
                    ], className="p-3 rounded bg-dark shadow mt-3"),
                    html.Button("ดาวน์โหลดข้อมูล CSV", id="btn-download", className="btn btn-primary mt-3")
                ], className="p-4 rounded bg-dark shadow"), width=12
            )
        ),
        
        # แถวแผนที่
        dbc.Row(
            dbc.Col(
                html.Div([ 
                    html.H4("แผนที่พื้นที่การพยากรณ์", className="text-white mb-3"),
                    dcc.Graph(figure=fig_map, className="shadow rounded mb-4")
                ], className="p-3 rounded bg-dark shadow mt-3"), width=12
            )
        ),
        
        dbc.Row([
            dbc.Col([ 
                dcc.Graph(figure=fig_pm25, className="shadow rounded mb-4"),
                dcc.Graph(figure=fig_humidity, className="shadow rounded mb-4"),
                dcc.Graph(figure=fig_temperature, className="shadow rounded mb-4"),
            ], width=7),
            
            dbc.Col([ 
                dbc.Row([ 
                    dbc.Col(
                        html.Div([ 
                            html.H4("Time Predictions", className="text-white mb-3"),
                            dcc.Tabs(
                                id='date-tabs',
                                value='all',
                                className='custom-tabs mb-3',
                                children=[
                                    dcc.Tab(label='ทั้งหมด', value='all', className='custom-tab'),
                                    dcc.Tab(label='วันนี้', value='today', className='custom-tab'),
                                    dcc.Tab(label='เลือกวันที่', value='specific', className='custom-tab'),
                                ],
                                colors={
                                    "border": "#444",
                                    "primary": "#ad7ff4",
                                    "background": "#333"
                                }
                            ),
                            html.Div(
                                dcc.DatePickerSingle(
                                    id='date-picker',
                                    min_date_allowed=None,
                                    max_date_allowed=None,
                                    initial_visible_month=None,
                                    date=None,
                                    display_format='YYYY-MM-DD',
                                    className='mb-3'
                                ),
                                id='date-picker-container',
                                style={'display': 'none'}
                            ),
                            html.Div(
                                id='prediction-content',
                                className='prediction-content',
                                style={"maxHeight": "400px", "overflowY": "auto"}
                            )
                        ], className="p-3 rounded bg-dark shadow"), width=12
                    )
                ]),
                
                # ส่วนรายละเอียดพื้นที่
                dbc.Row([
                    dbc.Col(
                        html.Div([ 
                            html.H4("รายละเอียดพื้นที่", className="text-white mb-3"),
                            dbc.Select(
                                id="area-selector",
                                options=[ 
                                    {"label": area["name"], "value": area["id"]} 
                                    for area in prediction_areas
                                ],
                                value=prediction_areas[0]["id"] if prediction_areas else None,
                                className="mb-3"
                            ),
                            html.Div(id="area-details")
                        ], className="p-3 rounded bg-dark shadow mt-3"), width=12
                    )
                ]), 
            ], width=5)
        ]),

        # เพิ่มส่วนดาวน์โหลดไฟล์
        dcc.Download(id="download-dataframe-csv")
    ], fluid=True, className="bg-dark text-light")
