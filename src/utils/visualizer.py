import plotly.express as px
import pandas as pd
import os
import uuid

def plot_with_plotly(columns, rows, x_axis, y_axis, chart_type="bar"):
    df = pd.DataFrame(rows, columns=columns)

    if chart_type == "bar":
        fig = px.bar(df, x=x_axis, y=y_axis)
    elif chart_type == "line":
        fig = px.line(df, x=x_axis, y=y_axis)
    elif chart_type == "pie":
        fig = px.pie(df, names=x_axis, values=y_axis)
    else:
        fig = px.bar(df, x=x_axis, y=y_axis)  # fallback

    os.makedirs("static/plots", exist_ok=True)
    plot_filename = f"{uuid.uuid4().hex}.html"
    html_path = os.path.join("static", "plots", plot_filename)
    fig.write_html(html_path, full_html=True, include_plotlyjs="cdn")
    return f"http://localhost:7861/plots/{plot_filename}"


    