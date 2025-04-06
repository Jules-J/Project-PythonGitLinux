import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Set theme with a professional look
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server  # For deployment if needed

def read_data():
    try:
        df = pd.read_csv("TTE.csv")
        # Ensure numeric conversion for price if needed
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        # Convert LastUpdated to datetime
        df['LastUpdated'] = pd.to_datetime(df['LastUpdated'], errors='coerce')
        return df
    except Exception as e:
        print(f"Error reading data: {e}")
        return pd.DataFrame(columns=['Price', 'LastUpdated'])

# Color scheme
colors = {
    'background': '#f9f9f9',
    'text': '#333333',
    'primary': '#007BFF',  # Blue
    'secondary': '#6c757d',
    'success': '#28a745',  # Green
    'danger': '#dc3545',   # Red
    'light': '#f8f9fa',
    'dark': '#343a40',
    'border': '#dee2e6'
}

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("TTE Stock Dashboard", style={'color': colors['dark'], 'textAlign': 'center'}),
        html.Hr(),
    ], style={'backgroundColor': colors['light'], 'padding': '20px', 'borderRadius': '5px'}),
    
    # Main content container
    html.Div([
        # Top row - Current price and daily change
        html.Div([
            # Current price card
            html.Div([
                html.H3("Current Price", style={'textAlign': 'center', 'color': colors['secondary']}),
                html.Div(
                    id='price-title',
                    style={
                        'border': f'2px solid {colors["border"]}',
                        'borderRadius': '5px',
                        'padding': '15px',
                        'textAlign': 'center',
                        'fontSize': '24px',
                        'backgroundColor': colors['light'],
                        'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)'
                    }
                ),
                html.Div(id='price-change', style={'textAlign': 'center', 'fontSize': '18px', 'marginTop': '10px'})
            ], className='six columns', style={'padding': '10px'}),
            
            # Key stats card
            html.Div([
                html.H3("Key Statistics", style={'textAlign': 'center', 'color': colors['secondary']}),
                html.Div(
                    id='key-stats',
                    style={
                        'border': f'2px solid {colors["border"]}',
                        'borderRadius': '5px',
                        'padding': '15px',
                        'backgroundColor': colors['light'],
                        'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)'
                    }
                )
            ], className='six columns', style={'padding': '10px'})
        ], className='row'),
        
        # Chart controls
        html.Div([
            html.Div([
                html.Label('Chart Type:'),
                dcc.RadioItems(
                    id='chart-type',
                    options=[
                        {'label': 'Line Chart', 'value': 'line'},
                        {'label': 'Candlestick', 'value': 'candlestick'}
                    ],
                    value='line',
                    labelStyle={'display': 'inline-block', 'marginRight': '15px'}
                ),
            ], className='six columns'),
            
            html.Div([
                html.Label('Time Period:'),
                dcc.Dropdown(
                    id='time-period',
                    options=[
                        {'label': 'Today', 'value': '1D'},
                        {'label': '1 Week', 'value': '1W'},
                        {'label': '1 Month', 'value': '1M'},
                        {'label': 'All Data', 'value': 'ALL'}
                    ],
                    value='ALL',
                    clearable=False
                )
            ], className='six columns')
        ], className='row', style={'marginTop': '20px', 'marginBottom': '20px'}),
        
        # Technical indicators
        html.Div([
            html.Label('Technical Indicators:'),
            dcc.Checklist(
                id='technical-indicators',
                options=[
                    {'label': '5-Day Moving Average', 'value': 'sma5'},
                    {'label': '10-Day Moving Average', 'value': 'sma10'},
                    {'label': '20-Day Moving Average', 'value': 'sma20'}
                ],
                value=[],
                labelStyle={'display': 'inline-block', 'marginRight': '15px'}
            )
        ], style={'marginBottom': '20px'}),
        
        # Chart
        html.Div([
            dcc.Graph(id='price-graph')
        ]),
        
        # Data table and toggle
        html.Div([
            html.Button(
                "Show Prices", 
                id="toggle-button", 
                n_clicks=0,
                style={
                    'backgroundColor': colors['primary'],
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'borderRadius': '5px',
                    'marginTop': '10px',
                    'marginBottom': '10px',
                    'cursor': 'pointer'
                }
            ),
            html.Div(
                dash_table.DataTable(
                    id='stock-table',
                    columns=[
                        {"name": "Date", "id": "LastUpdated"},
                        {"name": "Price ($)", "id": "Price"}
                    ],
                    data=[],
                    style_cell={'textAlign': 'center', 'padding': '10px'},
                    style_header={
                        'fontWeight': 'bold',
                        'backgroundColor': colors['light'],
                        'borderBottom': f'2px solid {colors["border"]}'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': colors['light']
                        }
                    ],
                    page_size=10
                ),
                id="table-container",
                style={'display': 'none'}  # hidden by default
            )
        ]),
        
        # Daily report
        html.Div([
            html.H3("Daily Report", style={'color': colors['secondary']}),
            html.Div(
                id='daily-report',
                style={
                    'border': f'2px solid {colors["border"]}',
                    'borderRadius': '5px',
                    'padding': '20px',
                    'marginTop': '10px',
                    'fontSize': '16px',
                    'backgroundColor': colors['light'],
                    'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)'
                }
            )
        ], style={'marginTop': '30px', 'marginBottom': '20px'}),
        
    ], style={'padding': '20px', 'backgroundColor': colors['background']}),
    
    # Footer
    html.Div([
        html.P("Data updates every 5 minutes"),
        dcc.Interval(id='interval-component', interval=300000, n_intervals=0),
    ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': colors['light'], 'marginTop': '20px'})
], style={'fontFamily': 'Arial, sans-serif', 'margin': '0 auto', 'maxWidth': '1200px'})

@app.callback(
    [Output('stock-table', 'data'),
     Output('price-graph', 'figure'),
     Output('price-title', 'children'),
     Output('daily-report', 'children'),
     Output('price-change', 'children'),
     Output('price-change', 'style'),
     Output('key-stats', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('chart-type', 'value'),
     Input('time-period', 'value'),
     Input('technical-indicators', 'value')]
)
def update_data(n, chart_type, time_period, technical_indicators):
    df = read_data()
    
    if df.empty:
        return [], {}, "No data available", "No data available", "", {}, ""
    
    # Filter data based on selected time period
    end_date = df['LastUpdated'].max()
    if time_period == '1D':
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_period == '1W':
        start_date = end_date - datetime.timedelta(days=7)
    elif time_period == '1M':
        start_date = end_date - datetime.timedelta(days=30)
    else:  # ALL
        start_date = df['LastUpdated'].min()
    
    df_filtered = df[df['LastUpdated'].between(start_date, end_date)]
    
    # Format for table
    table_data = df_filtered.copy()
    table_data['LastUpdated'] = table_data['LastUpdated'].dt.strftime('%Y-%m-%d %H:%M:%S')
    table_data = table_data[['LastUpdated', 'Price']].to_dict('records')
    
    # Prepare data for candlestick if needed
    if chart_type == 'candlestick':
        # Group by date for OHLC
        df_filtered['Date'] = df_filtered['LastUpdated'].dt.date
        ohlc = df_filtered.groupby('Date').agg({
            'Price': ['first', 'max', 'min', 'last']
        }).reset_index()
        ohlc.columns = ['Date', 'Open', 'High', 'Low', 'Close']
        ohlc['Date'] = pd.to_datetime(ohlc['Date'])
        
        # Create candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=ohlc['Date'],
            open=ohlc['Open'],
            high=ohlc['High'],
            low=ohlc['Low'],
            close=ohlc['Close'],
            name='OHLC'
        )])
    else:
        # Create line chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_filtered['LastUpdated'],
            y=df_filtered['Price'],
            mode='lines',
            name='TTE Stock Price',
            line=dict(color=colors['primary'], width=2)
        ))
    
    # Add moving averages if selected
    for ma in technical_indicators:
        if ma == 'sma5':
            window = 5
            color = 'rgba(255,165,0,0.7)'  # Orange
            name = '5-Day MA'
        elif ma == 'sma10':
            window = 10
            color = 'rgba(255,0,0,0.7)'  # Red
            name = '10-Day MA'
        else:  # sma20
            window = 20
            color = 'rgba(128,0,128,0.7)'  # Purple
            name = '20-Day MA'
        
        # Calculate moving average for the entire dataset to get meaningful values
        df['MA'] = df['Price'].rolling(window=window).mean()
        # Filter to the selected time period
        ma_data = df[df['LastUpdated'].between(start_date, end_date)]
        
        fig.add_trace(go.Scatter(
            x=ma_data['LastUpdated'],
            y=ma_data['MA'],
            mode='lines',
            name=name,
            line=dict(color=color, width=1.5)
        ))
    
    # Update layout
    fig.update_layout(
        title='TTE Stock Price Chart',
        xaxis=dict(
            title='Date',
            type='date',  # Explicitly set type to date to respect time intervals
            tickformat='%Y-%m-%d %H:%M',
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            )
        ),
        yaxis=dict(title='Price ($)'),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor=colors['light'],
        paper_bgcolor=colors['light'],
        font=dict(color=colors['text'])
    )
    
    # Last price and update info
    last_price = df['Price'].iloc[-1]
    last_updated = df['LastUpdated'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S')
    title_text = f"${last_price:.2f}"
    
    # Calculate price change and percentage
    prev_price = df['Price'].iloc[-2] if len(df) > 1 else last_price
    price_change = last_price - prev_price
    price_change_pct = (price_change / prev_price * 100) if prev_price != 0 else 0
    
    # Set color based on price movement
    if price_change > 0:
        change_color = colors['success']
        change_icon = "▲"
    elif price_change < 0:
        change_color = colors['danger']
        change_icon = "▼"
    else:
        change_color = colors['secondary']
        change_icon = "◆"
    
    price_change_text = f"{change_icon} ${abs(price_change):.2f} ({abs(price_change_pct):.2f}%) since last update"
    price_change_style = {'color': change_color, 'fontSize': '18px', 'fontWeight': 'bold'}
    
    # Calculate key statistics
    df['Date'] = df['LastUpdated'].dt.date
    today = datetime.datetime.today().date()
    
    # Get daily data
    df_today = df[df['Date'] == today]
    
    # Fallback to most recent date if no data for today
    if df_today.empty and not df.empty:
        latest_date = df['Date'].max()
        df_today = df[df['Date'] == latest_date]
    
    # Calculate key statistics
    if not df_today.empty:
        open_price = df_today['Price'].iloc[0]
        close_price = df_today['Price'].iloc[-1]
        high_price = df_today['Price'].max()
        low_price = df_today['Price'].min()
        day_change = close_price - open_price
        day_change_pct = (day_change / open_price * 100) if open_price != 0 else 0
        
        # Year-to-date calculation
        year_start = datetime.datetime(datetime.datetime.now().year, 1, 1).date()
        df_ytd = df[df['Date'] >= year_start]
        ytd_change_pct = 0
        if not df_ytd.empty:
            ytd_start = df_ytd['Price'].iloc[0]
            ytd_end = df_ytd['Price'].iloc[-1]
            ytd_change_pct = ((ytd_end - ytd_start) / ytd_start * 100) if ytd_start != 0 else 0
        
        # 52-week high/low
        one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).date()
        df_52w = df[df['Date'] >= one_year_ago]
        high_52w = df_52w['Price'].max() if not df_52w.empty else high_price
        low_52w = df_52w['Price'].min() if not df_52w.empty else low_price
        
        key_stats = html.Div([
            html.Div([
                html.Div([
                    html.Div("Open", style={'fontWeight': 'bold'}),
                    html.Div(f"${open_price:.2f}")
                ], className='three columns'),
                html.Div([
                    html.Div("High", style={'fontWeight': 'bold'}),
                    html.Div(f"${high_price:.2f}")
                ], className='three columns'),
                html.Div([
                    html.Div("Low", style={'fontWeight': 'bold'}),
                    html.Div(f"${low_price:.2f}")
                ], className='three columns'),
                html.Div([
                    html.Div("Close", style={'fontWeight': 'bold'}),
                    html.Div(f"${close_price:.2f}")
                ], className='three columns'),
            ], className='row'),
            html.Hr(style={'margin': '10px 0'}),
            html.Div([
                html.Div([
                    html.Div("Day Change", style={'fontWeight': 'bold'}),
                    html.Div(f"${day_change:.2f} ({day_change_pct:.2f}%)", 
                             style={'color': colors['success'] if day_change >= 0 else colors['danger']})
                ], className='four columns'),
                html.Div([
                    html.Div("YTD", style={'fontWeight': 'bold'}),
                    html.Div(f"{ytd_change_pct:.2f}%",
                             style={'color': colors['success'] if ytd_change_pct >= 0 else colors['danger']})
                ], className='four columns'),
                html.Div([
                    html.Div("52W Range", style={'fontWeight': 'bold'}),
                    html.Div(f"${low_52w:.2f} - ${high_52w:.2f}")
                ], className='four columns'),
            ], className='row')
        ])
    else:
        key_stats = "No statistics available"
    
    # For the daily report
    now = datetime.datetime.now(datetime.timezone.utc) # To take into accouunt that Amazon AWS uses UTC time
    if now.hour >= 18: #18h UTC is 8pm in Paris
        if not df_today.empty:
            # Compute metrics from today's data only.
            open_price = df_today['Price'].iloc[0]
            close_price = df_today['Price'].iloc[-1]
            high_price = df_today['Price'].max()
            low_price = df_today['Price'].min()
            volatility = df_today['Price'].std() if len(df_today) > 1 else 0
            evolution = ((close_price - open_price) / open_price * 100) if open_price != 0 else 0
            
            # Color coding for evolution
            evolution_color = colors['success'] if evolution >= 0 else colors['danger']
            
            daily_report = html.Div([
                html.Div([
                    html.Div([
                        html.P("Open Price:", style={'fontWeight': 'bold'}),
                        html.P(f"${open_price:.2f}")
                    ], className='three columns'),
                    html.Div([
                        html.P("Close Price:", style={'fontWeight': 'bold'}),
                        html.P(f"${close_price:.2f}")
                    ], className='three columns'),
                    html.Div([
                        html.P("High Price:", style={'fontWeight': 'bold'}),
                        html.P(f"${high_price:.2f}")
                    ], className='three columns'),
                    html.Div([
                        html.P("Low Price:", style={'fontWeight': 'bold'}),
                        html.P(f"${low_price:.2f}")
                    ], className='three columns'),
                ], className='row'),
                html.Div([
                    html.Div([
                        html.P("Volatility:", style={'fontWeight': 'bold'}),
                        html.P(f"{volatility:.2f}")
                    ], className='six columns'),
                    html.Div([
                        html.P("Evolution:", style={'fontWeight': 'bold'}),
                        html.P(f"{evolution:.2f}%", style={'color': evolution_color})
                    ], className='six columns'),
                ], className='row', style={'marginTop': '10px'})
            ])
        else:
            daily_report = "No data available for today's report."
    else:
        daily_report = "Daily report will be updated at 8pm."
        
    return table_data, fig, title_text, daily_report, price_change_text, price_change_style, key_stats

@app.callback(
    [Output("table-container", "style"),
     Output("toggle-button", "children")],
    Input("toggle-button", "n_clicks"),
    State("table-container", "style")
)
def toggle_table(n_clicks, current_style):
    if n_clicks is None or n_clicks % 2 == 0:
        # Even clicks: hide table
        return {'display': 'none'}, "Show Prices"
    else:
        # Odd number of clicks: show table
        return {'display': 'block'}, "Hide Prices"

if __name__ == '__main__':
    app.run(debug=True)