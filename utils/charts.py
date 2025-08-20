import plotly.express as px

def car_sales_chart(df):
    if df.empty:
        return None
    return px.pie(df, names="Car Type", values="Price", title="Car Wash Sales by Car Type")

def drink_sales_chart(df):
    if df.empty:
        return None
    return px.pie(df, names="Drink", values="Total", title="Drink Sales")
