import yfinance as yf
from pytrends.request import TrendReq
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from datetime import datetime

app = Dash(__name__)
server = app.server

def make_figure():
    start_date = "2015-01-01"
    end_date = datetime.today().strftime('%Y-%m-%d')
    search_terms = ["WW3", "Iran", "Israel"]

    sp500 = yf.download("^GSPC", start=start_date, end=end_date)['Close'].resample('W').mean()
    btc = yf.download("BTC-USD", start=start_date, end=end_date)['Close'].resample('W').mean()

    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(search_terms, timeframe=f'{start_date} {end_date}')
    gtrend = pytrends.interest_over_time().drop(columns='isPartial').resample('W').mean()

    df = pd.concat([sp500, btc, gtrend], axis=1).dropna()
    df.columns = ['S&P 500', 'BTC'] + search_terms

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['BTC'], name='BTC', yaxis='y1', line=dict(color="orange")))
    fig.add_trace(go.Scatter(x=df.index, y=df['S&P 500'], name='S&P 500', yaxis='y2', line=dict(color="white")))
    for term in search_terms:
        norm = df[term] / df[term].max() * 100
        fig.add_trace(go.Scatter(x=df.index, y=norm, name=term, yaxis='y3', line=dict(width=1)))

    fig.update_layout(
        title="BTC & S&P 500 vs Google Trends",
        xaxis=dict(title="Date", showgrid=False),
        yaxis=dict(title="BTC (log)", type="log", side="left", showgrid=False),
        yaxis2=dict(title="S&P 500 (log)", type="log", overlaying="y", side="left", position=0.05, showgrid=False),
        yaxis3=dict(title="Search Trend (0–100)", overlaying="y", side="right", showgrid=False, tickmode="linear", tick0=0, dtick=20, range=[0, 100]),
        height=600,
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white")
    )

    print("Chart generated successfully", flush=True)
    return fig

app.layout = html.Div([
    html.H1("Market vs Google Search Trends"),
    dcc.Graph(figure=make_figure())
])

print("Layout initialized", flush=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)
