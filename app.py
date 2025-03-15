import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from flask import Flask
import os
from datetime import datetime, timedelta
import plotly.express as px
import json


def create_layout(fig_map, fig_pm25, fig_humidity, fig_temperature, prediction_areas):
    # คำนวณค่าเฉลี่ยของข้อมูล
    avg_pm25 = data['PM 2.5']['df'][data['PM 2.5']['col']].mean()
    avg_humidity = data['Humidity']['df'][data['Humidity']['col']].mean()
    avg_temperature = data['Temperature']['df'][data['Temperature']['col']].mean()

    return dbc.Container([
   # ส่วนหัว Dashboard
dbc.Row(
    dbc.Col(
        html.Div([
            html.H2("Dashboard การพยากรณ์", className="text-white neumorphism-heading"),
            html.P("ข้อมูลพยากรณ์ PM 2.5, ความชื้น และ อุณหภูมิ (7 วัน)", className="text-white neumorphism-text"),
        ], className="p-4 rounded bg-dark neumorphism-card shadow"), width=12
    )
),

        
        # แถวแผนที่
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H4("แผนที่พื้นที่การพยากรณ์", className="text-white mb-3"),
                    dcc.Graph(figure=fig_map, className="shadow rounded mb-4", id="prediction-map")
                ], className="p-3 rounded bg-dark shadow mt-3"), width=12
            )
        ),
        
        # แถวแสดงค่าเฉลี่ย (อยู่ด้านล่างแผนที่)
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H4("ค่าเฉลี่ย 7 วัน", className="text-white mb-3"),
                    dbc.Row([
                        dbc.Col(
                            html.Div([
                                html.P("PM 2.5", className="text-white mb-1"),
                                html.P(f"{avg_pm25:.2f} μg/m³", className="text-white h4")
                            ], className="p-3 rounded bg-secondary text-center shadow"), width=4
                        ),
                        dbc.Col(
                            html.Div([
                                html.P("ความชื้น", className="text-white mb-1"),
                                html.P(f"{avg_humidity:.2f}%", className="text-white h4")
                            ], className="p-3 rounded bg-secondary text-center shadow"), width=4
                        ),
                        dbc.Col(
                            html.Div([
                                html.P("อุณหภูมิ", className="text-white mb-1"),
                                html.P(f"{avg_temperature:.2f}°C", className="text-white h4")
                            ], className="p-3 rounded bg-secondary text-center shadow"), width=4
                        ),
                    ])
                ], className="p-3 rounded bg-dark shadow mt-3"), width=12
            )
        ),
        
        # แถวกราฟและคอนเทนต์ด้านขวา
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
                            
                            # แท็บสำหรับเลือกวันที่
                            dcc.Tabs(
                                id='date-tabs',
                                value='all',
                                className='custom-tabs mb-3',
                                children=[
                                    dcc.Tab(label='ทั้งหมด', value='all', className='custom-tab'),
                                    dcc.Tab(label='รายละเอียดพื้นที่', value='today', className='custom-tab'),
                                    dcc.Tab(label='7 วันที่ทำนาย', value='specific', className='custom-tab'),
                                ],
                                colors={
                                    "border": "#444",
                                    "primary": "#ad7ff4",
                                    "background": "#333"
                                }
                            ),
                            
                            # DatePicker สำหรับเลือกวันที่เฉพาะ (จะปรากฏเมื่อเลือกแท็บ 'specific')
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
                            
                            # พื้นที่แสดงผลค่าพยากรณ์ (Scrollable)
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
        ])
    ], fluid=True, className="bg-dark text-light")



server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.DARKLY])

# ----------------------------
# โหลดไฟล์ CSV โดยใช้ path ที่ถูกต้อง
# ----------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))

file_paths = {
    "PM 2.5": os.path.join(script_dir, r"D:\dash\pm_2.5_Term_Project\pm_2.5\predicted_pm25.csv"),
    "Humidity": os.path.join(script_dir, r"D:\dash\pm_2.5_Term_Project\pm_2.5\predicted_humidity.csv"),
    "Temperature": os.path.join(script_dir, r"D:\dash\pm_2.5_Term_Project\pm_2.5\predicted_temperature.csv"),
}

# ----------------------------
# ข้อมูลพื้นที่พยากรณ์
# ----------------------------
prediction_areas = [
    {
        "id": "area1",
        "name": "สถานีเทศบาลนครหาดใหญ่",
        "coordinates": [100.4722, 7.0086],  # [longitude, latitude]
        "radius": 5000,
        "predictions": {
            "pm25": 3.7,
            "humidity": 65.2,
            "temperature": 32.5
        }
    },
]

# ----------------------------
# โหลดข้อมูล CSV และจัดเก็บลงตัวแปร data
# ----------------------------
data = {}

for key, path in file_paths.items():
    try:
        df = pd.read_csv(path)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["date"] = df["datetime"].dt.date
        prediction_col = [col for col in df.columns if "predict" in col.lower()]
        if prediction_col:
            data[key] = {"df": df, "col": prediction_col[0]}
        else:
            print(f"Warning: No prediction column found in file {path}")
            print(f"Available columns: {df.columns.tolist()}")
    except FileNotFoundError:
        print(f"Error: File not found at {path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Script directory: {script_dir}")
        raise

# ----------------------------
# ฟังก์ชันกรองข้อมูลตามจำนวนวัน
# ----------------------------
def filter_by_days(df, days=7):
    today = df["datetime"].max()
    start_date = today - timedelta(days=days-1)
    return df[(df["datetime"] >= start_date) & (df["datetime"] <= today)]

# ----------------------------
# ฟังก์ชันสร้างกราฟ
# ----------------------------
def create_graph(title, key, color, days=7):
    filtered_df = filter_by_days(data[key]["df"], days)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_df["datetime"],
        y=filtered_df[data[key]["col"]],
        fill='tozeroy',
        mode='lines',
        line=dict(color=color, width=3),
        fillcolor=color.replace("1)", "0.3)")
    ))
    fig.update_layout(
        title=title, 
        xaxis_title="เวลา", 
        yaxis_title=key,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        height=300
    )
    return fig

# ----------------------------
# ฟังก์ชันสร้างแผนที่ (ใช้สไตล์ Open Street Map)
# ----------------------------
def create_map():
    avg_lat = sum(area["coordinates"][1] for area in prediction_areas) / len(prediction_areas)
    avg_lon = sum(area["coordinates"][0] for area in prediction_areas) / len(prediction_areas)
    
    fig = go.Figure()

    for area in prediction_areas:
        lat, lon = area["coordinates"][1], area["coordinates"][0]
        pm25 = area["predictions"]["pm25"]
        humidity = area["predictions"]["humidity"]
        temperature = area["predictions"]["temperature"]
        
        if pm25 <= 25:
            color = "green"
        elif pm25 <= 50:
            color = "blue"
        elif pm25 <= 100:
            color = "yellow"
        elif pm25 <= 150:
            color = "orange"
        else:
            color = "red"
        
        fig.add_trace(go.Scattermapbox(
            lat=[lat],
            lon=[lon],
            mode='markers',
            marker=dict(size=20, color=color, opacity=0.7),
            text=f"{area['name']}<br>PM2.5: {pm25} μg/m³<br>ความชื้น: {humidity}%<br>อุณหภูมิ: {temperature}°C",
            hoverinfo="text",
            name=area["name"]
        ))
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",  # ใช้สไตล์ Open Street Map
            center=dict(lat=avg_lat, lon=avg_lon),
            zoom=11
        ),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(33, 37, 41, 0.8)",
            font=dict(color="white")
        )
    )
    
    return fig

# สร้างกราฟและแผนที่ทั้งหมด
fig_pm25 = create_graph("พยากรณ์ค่า PM 2.5", "PM 2.5", "rgba(173, 127, 244, 1)")
fig_humidity = create_graph("พยากรณ์ค่าความชื้น", "Humidity", "rgba(100, 200, 255, 1)")
fig_temperature = create_graph("พยากรณ์ค่าอุณหภูมิ", "Temperature", "rgba(255, 100, 100, 1)")
fig_map = create_map()

# กำหนดเลย์เอาต์หลักของแอป
app.layout = create_layout(fig_map, fig_pm25, fig_humidity, fig_temperature, prediction_areas)

# ----------------------------
# Callback สำหรับแสดง/ซ่อน DatePicker ตามแท็บที่เลือก
# ----------------------------
@app.callback(
    [Output("date-picker-container", "style"),
     Output("date-picker", "min_date_allowed"),
     Output("date-picker", "max_date_allowed"),
     Output("date-picker", "initial_visible_month"),
     Output("date-picker", "date")],
    [Input("date-tabs", "value")]
)
def toggle_date_picker(selected_tab):
    pm_df = data["PM 2.5"]["df"]
    min_date = pm_df["datetime"].min().date()
    max_date = pm_df["datetime"].max().date()
    
    if selected_tab == "specific":
        return (
            {"display": "block"},
            min_date,
            max_date,
            max_date,
            max_date
        )
    else:
        return (
            {"display": "none"},
            None,
            None,
            None,
            None
        )

# ----------------------------
# Callback สำหรับอัปเดตเนื้อหาค่าพยากรณ์ตามวันที่ที่เลือก
# ----------------------------
@app.callback(
    Output('prediction-content', 'children'),
    [Input('date-tabs', 'value'),
     Input('date-picker', 'date')]
)
def update_prediction_content(selected_tab, selected_date):
    df = data["PM 2.5"]["df"]
    humidity_df = data["Humidity"]["df"]
    temp_df = data["Temperature"]["df"]
    
    pred_col = data["PM 2.5"]["col"]
    humidity_col = data["Humidity"]["col"]
    temp_col = data["Temperature"]["col"]
    
    if selected_tab == 'today':
        today = pd.Timestamp.now().date()
        filtered_df = df[df['datetime'].dt.date == today]
        filtered_humidity = humidity_df[humidity_df['datetime'].dt.date == today]
        filtered_temp = temp_df[temp_df['datetime'].dt.date == today]
    elif selected_tab == 'specific' and selected_date:
        specific_date = pd.to_datetime(selected_date).date()
        filtered_df = df[df['datetime'].dt.date == specific_date]
        filtered_humidity = humidity_df[humidity_df['datetime'].dt.date == specific_date]
        filtered_temp = temp_df[temp_df['datetime'].dt.date == specific_date]
    else:
        filtered_df = filter_by_days(df, 7)
        filtered_humidity = filter_by_days(humidity_df, 7)
        filtered_temp = filter_by_days(temp_df, 7)
    
    filtered_df['date'] = filtered_df['datetime'].dt.date
    filtered_humidity['date'] = filtered_humidity['datetime'].dt.date
    filtered_temp['date'] = filtered_temp['datetime'].dt.date
    
    date_groups = filtered_df.groupby('date')
    content_items = []
    
    for date, group in date_groups:
        date_str = date.strftime('%Y-%m-%d')
        time_rows = []
        time_rows.append(
            html.Div([ 
                html.Div("เวลา", className="col-3 fw-bold text-light"),
                html.Div("PM2.5", className="col-3 fw-bold text-light text-end"),
                html.Div("ความชื้น", className="col-3 fw-bold text-light text-end"),
                html.Div("อุณหภูมิ", className="col-3 fw-bold text-light text-end")
            ], className="row mb-2 border-bottom pb-2")
        )
        
        for _, row in group.sort_values(by="datetime").iterrows():
            time_str = row['datetime'].strftime('%H:%M')
            pm_value = row[pred_col]
            
            humidity_value = filtered_humidity[
                (filtered_humidity['datetime'].dt.date == date) & 
                (filtered_humidity['datetime'].dt.hour == row['datetime'].hour)
            ][humidity_col].values
            
            temp_value = filtered_temp[
                (filtered_temp['datetime'].dt.date == date) & 
                (filtered_temp['datetime'].dt.hour == row['datetime'].hour)
            ][temp_col].values
            
            humidity_display = f"{humidity_value[0]:.2f}" if len(humidity_value) > 0 else "N/A"
            temp_display = f"{temp_value[0]:.2f}" if len(temp_value) > 0 else "N/A"
            
            color_class = ""
            if pm_value > 150:
                color_class = "text-danger"
            elif pm_value > 50:
                color_class = "text-warning"
            else:
                color_class = "text-success"
                
            time_rows.append(
                html.Div([
                    html.Div(f"{time_str}", className="col-3 text-light"),
                    html.Div(f"{pm_value:.2f}", className=f"col-3 text-end {color_class}"),
                    html.Div(humidity_display, className="col-3 text-end text-info"),
                    html.Div(temp_display, className="col-3 text-end text-danger")
                ], className="row mb-1")
            )
        
        content_items.append(
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.Div([ 
                            html.Span(date_str, className="fw-bold"),
                            html.Small(f" ({len(group)} ค่าพยากรณ์)", className="text-muted ms-2")
                        ]),
                        className="fw-bold"
                    ),
                    dbc.CardBody(time_rows)
                ],
                className="mb-3 bg-dark border-secondary"
            )
        )
    
    if content_items:
        return html.Div(content_items)

# ----------------------------
# Callback สำหรับดาวน์โหลดข้อมูลเป็น CSV
# ----------------------------
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-download", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv(n_clicks):
    pm_df = data["PM 2.5"]["df"].copy()
    humidity_df = data["Humidity"]["df"].copy()
    temp_df = data["Temperature"]["df"].copy()
    
    pm_df.rename(columns={data["PM 2.5"]["col"]: "pm25_prediction"}, inplace=True)
    humidity_df.rename(columns={data["Humidity"]["col"]: "humidity_prediction"}, inplace=True)
    temp_df.rename(columns={data["Temperature"]["col"]: "temperature_prediction"}, inplace=True)
    
    pm_df = pm_df[["datetime", "date", "pm25_prediction"]]
    humidity_df = humidity_df[["datetime", "humidity_prediction"]]
    temp_df = temp_df[["datetime", "temperature_prediction"]]
    
    merged_df = pd.merge(pm_df, humidity_df, on="datetime", how="left")
    merged_df = pd.merge(merged_df, temp_df, on="datetime", how="left")
    
    merged_df["date"] = merged_df["datetime"].dt.strftime('%Y-%m-%d')
    merged_df["time"] = merged_df["datetime"].dt.strftime('%H:%M')
    
    final_df = merged_df[["date", "time", "pm25_prediction", "humidity_prediction", "temperature_prediction"]]
    
    return dcc.send_data_frame(final_df.to_csv, "predictions_data.csv", index=False)

# ----------------------------
# Callback สำหรับอัปเดตรายละเอียดพื้นที่ตามที่เลือก
# ----------------------------
@app.callback(
    Output("area-details", "children"),
    [Input("area-selector", "value")]
)
def update_area_details(area_id):
    selected_area = next((area for area in prediction_areas if area["id"] == area_id), None)
    
    if not selected_area:
        return html.P("ไม่พบข้อมูลพื้นที่ที่เลือก", className="text-white")
    
    lat, lon = selected_area["coordinates"][1], selected_area["coordinates"][0]
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H5(selected_area["name"], className="mb-0 text-white"),
                className="bg-secondary"
            ),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(html.Span("พิกัด:", className="fw-bold"), width=4),
                    dbc.Col(html.Span(f"Lat: {lat}, Lon: {lon}"), width=8)
                ])
            ])
        ],
        className="mb-3 bg-dark border-secondary"
    )


if __name__ == '__main__':
    app.run_server(debug=True)
