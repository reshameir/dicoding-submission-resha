import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_performance_df(df):
    perfromance_df = df.resample(rule='M', on='dteday').agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    perfromance_df.index = perfromance_df.index.strftime('%Y-%m')
    perfromance_df = perfromance_df.reset_index()
    perfromance_df.rename(columns={
        "dteday": "tanggal",
        "cnt": "total_rental"
    }, inplace=True)

    return perfromance_df

def create_daily_df(df):
    daily_df = df.groupby(by="weekday").cnt.sum().sort_values(ascending=False).reset_index()

    day_mapping = {
        0: "Monday",
        1: "Tuesday",
        2: "wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    for index, row in daily_df.iterrows():
        daily_df.loc[index, "day"] = day_mapping[row["weekday"]]

    return daily_df

def create_holiday_df(df):
    holiday_df = df.groupby(by="holiday").agg({
        'cnt': 'sum',
        'holiday': 'count'
    }).rename(columns={"holiday": "holiday_count"})
    holiday_df["average"] = holiday_df["cnt"]/holiday_df["holiday_count"]
    holiday_df['is_holiday'] = holiday_df.index.map({0: 'Hari Biasa', 1: 'Liburan'})
    holiday_df = holiday_df.sort_values(by='cnt', ascending=False).reset_index()

    return holiday_df

def create_weather_df(df):
    weather_df = df.groupby(by="weathersit").cnt.sum().sort_values(ascending=False).reset_index()
    weather_df['the_weather_is'] = weather_df.index.map({0: 'Sunny', 1: 'Cloudy', 2: 'Drizzly '})

    return weather_df

def create_hr_period_df(df):
    hr_period_df = df.groupby(by="hr_period").cnt.sum().reset_index()

    return hr_period_df

day_df = pd.read_csv("day_df.csv")
hour_df = pd.read_csv("new_hour_df.csv")

day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()
 
with st.sidebar:

    st.title('Filter Data')
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_day_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

main_hour_df = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                (hour_df["dteday"] <= str(end_date))]

performance_df = create_performance_df(main_day_df)
daily_df = create_daily_df(main_day_df)
holiday_df = create_holiday_df(main_day_df)
weather_df = create_weather_df(main_day_df)
hr_period_df = create_hr_period_df(main_hour_df)

st.header('Resha\'s Bike Sharing Dataset Dashboard')

st.subheader('Bike Rent Performances')
 
col1, col2 = st.columns(2)
 
with col1:
    total_rent = day_df.cnt.sum()
    st.metric("Total Rent", value=total_rent)
 
with col2:
    avg_rent = day_df.cnt.mean()
    avg_rent = "%.2f" % avg_rent
    st.metric("Average Rent", value=avg_rent+" per day")

plt.figure(figsize=(20, 5))
plt.plot(performance_df["tanggal"], performance_df["total_rental"], marker='o', linewidth=2, color="#72BCD4")
plt.title("Monthly Total Rent Performances", loc="center", fontsize=20)
plt.xticks(fontsize=10, rotation=45)
plt.yticks(fontsize=10)
plt.xlabel("Year-Month")
plt.ylabel("Total Rental")
st.pyplot(plt)

st.subheader('The Day with the Highest Total Rent')

plt.figure(figsize=(10, 5))
colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="cnt",
    y="day",
    data=daily_df.sort_values(by="cnt", ascending=False),
    palette=colors_,
)
plt.title("Total Bike Rent by Day", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='y', labelsize=12)
st.pyplot(plt)

st.subheader('The influence of Weather and Holidays on Bike Rent Performance')

col1, col2 = st.columns(2)

with col1:
    colors = ["#72BCD4", "#D3D3D3"]

    plt.figure(figsize=(10, 5))

    sns.barplot(
        y="average",
        x="is_holiday",
        data=holiday_df,
        palette=colors
    )
    plt.title("Holidays's influence on Bike Rent", loc="center", fontsize=15)
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=12)
    st.pyplot(plt)

with col2:
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3"]

    plt.figure(figsize=(10, 5))

    sns.barplot(
        y="cnt",
        x="the_weather_is",
        data=weather_df,
        palette=colors
    )
    plt.title("weather's influence on Bike Rent", loc="center", fontsize=15)
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=12)
    st.pyplot(plt)

st.subheader('When is the time period when the most bike rentals occur?')

colors = ["#72BCD4"]

plt.figure(figsize=(10, 5))

sns.barplot(
    y="cnt",
    x="hr_period",
    data=hr_period_df,
    palette=colors
)
plt.title("Bike Rental Performance in each Time Period", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='x', labelsize=12)
st.pyplot(plt)