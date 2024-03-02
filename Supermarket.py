import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from wordcloud import WordCloud
import datetime 
from io import BytesIO


# Set the icon for the title of the page
st.set_page_config(
    page_title="CamboMarket",
    page_icon="👋",
    layout="wide"
)


def filter_customers(customer_type, df):
    
    quantity_median = df['Quantity'].median()
    total_median = df['Total'].median()
    
    if customer_type == 'Low-value customers':
        filtered_df = df[(df['Quantity'] > quantity_median) & (df['Total'] < total_median)]
    
    elif customer_type == 'High-value customers':
        filtered_df = df[(df['Quantity'] < quantity_median) & (df['Total'] > total_median)]
        
    elif customer_type == 'High-risk customers':
        filtered_df = df[(df['Total'] > total_median) & (df['Rating'] < 5)]
        
    return filtered_df.sort_values(by='Total', ascending=False)
        

@st.cache_data
def load_data():
    df = pd.read_csv('data/supermarket_sales_raw.csv')
    return df


# Set theme
st.title('🥇 CamboMarket')
st.header('Nourishing Your Lifestyle, Cultivating Community Growth')
st.write('''This data set includes the sales data of a supermarket in Yangon, 
         Naypyitaw and Mandalay in Myanmar in the past three months. By analyzing this dataset, 
         l want to explore the impact of diferent factors on customer consumption and understand 
         customersconsumption habits, so as to guide the supermarket's operational strategies and increase sales''')

st.divider()


# The following is the sidebar widget area
option1 = st.sidebar.multiselect(
    'City',
    ['Yangon', 'Naypyitaw', 'Mandalay'],
    ['Yangon', 'Naypyitaw', 'Mandalay'])

first_day = datetime.date(2019, 1, 1)
last_day = datetime.date(2019, 3, 31)
date_value = st.sidebar.date_input( 
    "Date",
    (first_day, last_day),
    first_day,
    last_day,
    format="MM/DD/YYYY",
)

option2 = st.sidebar.multiselect(
    'Membership',
    ['Member', 'Normal'],
    ['Member', 'Normal'])

option3 = st.sidebar.multiselect(
    'Gender',
    ['Male', 'Female'],
    ['Male', 'Female'])



#The following is the DashBody part on the right
#--------------------zc Part-------------------------------------------

col = st.columns([3, 1])

with col[0]:
    # Create three subcontainers in the first column
    col_sub = st.columns([2, 2.2, 1])
    data = load_data()
    data["Date"] = pd.to_datetime(data["Date"])
    # catch the error when filtering
    try:
        mask = (data["Date"]>= pd.to_datetime(date_value[0]) ) & (data["Date"]<= pd.to_datetime(date_value[1])) & (data["City"].isin(option1) ) & (data["Customer type"].isin(option2) ) & (data["Gender"].isin(option3) )
        lastest_data = data[mask]
        col_sub[0].metric("💵Total sales", f"${round(lastest_data['Total'].sum())}")
        col_sub[1].metric("💰Total revenue", f"${round(lastest_data['gross income'].sum())}")
        col_sub[2].metric("🎗Avg rating", round(lastest_data['Rating'].mean(),2 ))

    except Exception as e:
        print("something wrong")
        # st.write(e)    # just for debug

        # when selecting data, give a loading
        # with st.spinner('Wait for it...'):
        #     time.sleep(15)
    
    st.divider()
    
    
#----------------------zc Part---------------------------------------

    # Show wordcloud 
    df = load_data()
    wordcloud = WordCloud(width=770, height=400, background_color='white').generate(' '.join(df['Product line']))
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout(pad=0)
    
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    st.image(buf, use_column_width=True)
    st.divider()
    

    # Show line chart
    df['Date'] = pd.to_datetime(df['Date'])
    
    grouped_sales = df.groupby([df['Date'].dt.to_period('M'), 'Customer type'])['Total'].sum().unstack()
    grouped_sales = grouped_sales.fillna(0) 
    grouped_sales.index = grouped_sales.index.to_timestamp()
    
    st.header('Sales Trend Visualization')
    
    fig, ax = plt.subplots(figsize=(9, 5.15), facecolor='white')
    ax.set_facecolor('white')
    
    ax.plot(grouped_sales.index, grouped_sales['Member'], label='Member', color='red', linestyle='--')
    ax.plot(grouped_sales.index, grouped_sales['Normal'], label='Normal', color='green', linestyle='--')
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45)
    
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Total Revenue', fontsize=12)
    ax.set_title('Monthly Sales Trend', fontsize=16)
    ax.tick_params(axis='both', which='major', labelsize=10) 

    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    ax.grid(True, color='lightgray', linestyle='--', linewidth=0.5)
    
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1)
        spine.set_edgecolor('black')
        spine.set_edgecolor('lightgrey')
    
    st.pyplot(fig)
    st.divider()
    
    
# Print table 
options = {
'Low-value customers': 'The quantity of goods purchased in a single transaction is exceeds 50% of other customers, the profit is lower than 50% of other customers',
'High-value customers': 'The quantity of goods purchased in a single transaction is less than 50% of other customers, but the profit is greater than 50% of other customers',
'High-risk customers': 'The total sales exceeding 50% of other customers, but with a rating below 5.0'
}

st.header('Customer segmentation')

col1, col2 = st.columns([0.6, 1])
with col1:  
    customer_type = st.radio("**Select a specific audience**", list(options.keys()))
    
with col2:
    df = load_data()
    filtered_df = filter_customers(customer_type, df)
    if customer_type:
        st.info(f"**{customer_type}**: {options[customer_type]}")
     
st.dataframe(filtered_df)
    

#----------------------zc Part---------------------------------------

with col[1]:
    st.subheader("Sales Rank")
    data = load_data()
    data["Date"] = pd.to_datetime(data["Date"])
    # catch the error when filtering
    try:
        # filter the data
        mask = (data["Date"]>= pd.to_datetime(date_value[0]) ) & (data["Date"]<= pd.to_datetime(date_value[1])) & (data["City"].isin(option1) ) & (data["Customer type"].isin(option2) ) & (data["Gender"].isin(option3) )
        lastest_data = data[mask]
        # Sort the data
        plot_data = lastest_data.groupby("Product line")["Total"].sum().reset_index().sort_values(by='Total', ascending=False)

        container = st.container(border=True)
        
        # provide a better UI for ranking
        index_count = 0
        for index, row in plot_data.iterrows():
            if index_count == 0:
                color = "#339900"
                icont = "🥇"
            elif index_count == 5:
                color = "#FF3300"
                icont = ""
            else:
                color = "#000000"
                icont= ""
            container.write(f"{icont}<span style='color:{color};font-weight:bold;font-size:14px;'>{row['Product line']}:</span><span style='font-size:14px;float:right;color:{color};'>${round(row['Total'])}</span>",unsafe_allow_html=True)
            index_count = index_count + 1


    except Exception as e:
        print("something wrong")
        # st.write(plot_data)    # just for debug
        
        
    st.divider()
    
    
    st.subheader("Revenue Rank")
    data = load_data()
    data["Date"] = pd.to_datetime(data["Date"])
    # catch the error when filtering
    try:
        # filter the data
        mask = (data["Date"]>= pd.to_datetime(date_value[0]) ) & (data["Date"]<= pd.to_datetime(date_value[1])) & (data["City"].isin(option1) ) & (data["Customer type"].isin(option2) ) & (data["Gender"].isin(option3) )
        lastest_data = data[mask]
        # Sort the data
        plot_data = lastest_data.groupby("Product line")["gross income"].sum().reset_index().sort_values(by='gross income', ascending=False)

        container = st.container(border=True)
        
        # provide a better UI for ranking
        index_count = 0
        for index, row in plot_data.iterrows():
            if index_count == 0:
                color = "#339900"
                icont = "🥇"
            elif index_count == 5:
                color = "#FF3300"
                icont = ""
            else:
                color = "#000000"
                icont= ""
            container.write(f"{icont}<span style='color:{color};font-weight:bold;font-size:14px;'>{row['Product line']}:</span><span style='font-size:14px;float:right;color:{color};'>${round(row['gross income'])}</span>",unsafe_allow_html=True)
            index_count = index_count + 1


    except Exception as e:
        print("something wrong")
        # st.write(plot_data)    # just for debug
        
        
    st.divider()


    st.subheader("Rating Rank")
    data = load_data()
    data["Date"] = pd.to_datetime(data["Date"])
    # catch the error when filtering
    try:
        # filter the data
        mask = (data["Date"]>= pd.to_datetime(date_value[0]) ) & (data["Date"]<= pd.to_datetime(date_value[1])) & (data["City"].isin(option1) ) & (data["Customer type"].isin(option2) ) & (data["Gender"].isin(option3) )
        lastest_data = data[mask]
        # Sort the data
        plot_data = lastest_data.groupby("Product line")["Rating"].mean().reset_index().sort_values(by='Rating', ascending=False)

        container = st.container(border=True)
        
        # provide a better UI for ranking
        index_count = 0
        for index, row in plot_data.iterrows():
            if index_count == 0:
                color = "#339900"
                icont = "🥇"
            elif index_count == 5:
                color = "#FF3300"
                icont = ""
            else:
                color = "#000000"
                icont= ""
            container.write(f"{icont}<span style='color:{color};font-weight:bold;font-size:14px;'>{row['Product line']}:</span><span style='font-size:14px;float:right;color:{color};'>{round(row['Rating'],2)}</span>",unsafe_allow_html=True)
            index_count = index_count + 1


    except Exception as e:
        print("something wrong")
        # st.write(plot_data)    # just for debug
        
#----------------------zc Part---------------------------------------
