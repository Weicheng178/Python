import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime 


# 设置页面的标题的图标
st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    layout="wide"
)

# 敏感客户和风险客户分析表格
def filter_customers(customer_type, df):
    
    total_25th_percentile = df['Total'].quantile(0.25)
    total_75th_percentile = df['Total'].quantile(0.75)
    
    if customer_type == 'Total Customer':
        # 展示所有客户
        filtered_df = df
    elif customer_type == 'Sensitive Customer':
        # 展示敏感客户
        filtered_df = df[(df['Rating'] > 7) & 
                         (df['Customer type'] == 'Member') & 
                         (df['Total'] >= total_75th_percentile)]
    else:
        # 展示风险客户
        filtered_df = df[(df['Rating'] < 5) & 
                         (df['Customer type'] == 'Normal') & 
                         (df['Total'] <= total_25th_percentile)]
        
    filtered_df = filtered_df.sort_values(by='Total', ascending=False)
    return filtered_df
        

# 打印原表格
@st.cache_data
def load_data():
    df = pd.read_csv('data/supermarket_sales_raw.csv')
    return df


# 设置主题
st.title('My portfolio')
st.header('Here is my portfolio. Don\'t hesitate to contact me for more information.')

st.subheader('About Me')
st.write('I am a Data Scientist with a background in Business and Datascience.  n\
    From data engineering to Business Intelligence, always looking for new opportunities and insights')


# 以下是侧边栏小部件区域

# 城市多选小部件
option1 = st.sidebar.multiselect(
    'City',
    ['Yangon', 'Naypyitaw', 'Mandalay'],
    ['Yangon', 'Naypyitaw', 'Mandalay'])

# 时间小部件
first_day = datetime.date(2019, 1, 1)
last_day = datetime.date(2019, 3, 31)
d = st.sidebar.date_input(
    "Date",
    (first_day, datetime.date(2019, 1, 1)),
    first_day,
    last_day,
    format="MM/DD/YYYY",
)

# 会员资格多选小部件
option2 = st.sidebar.multiselect(
    'Membership',
    ['Member', 'Normal'],
    ['Member', 'Normal'])

# 性别多选小部件
option3 = st.sidebar.multiselect(
    'Gender',
    ['Male', 'Female'],
    ['Male', 'Female'])




# 以下是右边DashBody部分
col = st.columns([3, 1])

# 第一列数据
with col[0]:
    
    st.header("Column 1")
    st.write("This is some content in column 1.")

    # 在第一列中创建三个子容器
    col_sub = st.columns([2, 2.2, 1])
    col_sub[0].metric("Total sales", "€420")
    col_sub[1].metric("Total revenue", "€420")
    col_sub[2].metric("Avg rating", "7.8")
    
    
    
    # 折线图
    df = load_data()
    df['Date'] = pd.to_datetime(df['Date'])
    
    grouped_sales = df.groupby([df['Date'].dt.to_period('M'), 'Customer type'])['Total'].sum().unstack()
    grouped_sales = grouped_sales.fillna(0)  # 用0填充NaN值
    grouped_sales.index = grouped_sales.index.to_timestamp()
    
    st.title('Sales Trend Visualization')
    
    fig, ax = plt.subplots(figsize=(10, 6))  
    
    ax.plot(grouped_sales.index, grouped_sales['Member'], label='Member', color='blue')
    ax.plot(grouped_sales.index, grouped_sales['Normal'], label='Normal', color='green')
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45)
    
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Total Revenue', fontsize=12)
    ax.set_title('Monthly Sales Trend', fontsize=16)
    ax.tick_params(axis='both', which='major', labelsize=10) 

    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    
    st.pyplot(fig)


    

    # 表格打印
    st.header('Customer segmentation')
    
    options = ["Total Customer",'Sensitive Customer','Risk Customer']
    customer_type = st.radio("Choose a Customer Type", options)
    
    df = load_data()
    filtered_df = filter_customers(customer_type, df)
    
    # 显示表格
    st.dataframe(filtered_df)
    

sales_rank_data = {"Product1": "€420", "Product2": "€420", "Product3": "€420",
                   "Product4": "€420", "Product5": "€420", "Product6": "€420"}
revenue_rank_data = {"Product1": "€420", "Product2": "€420", "Product3": "€420",
                   "Product4": "€420", "Product5": "€420", "Product6": "€420"}
rating_rank_data = {"Product1": "€420", "Product2": "€420", "Product3": "€420",
                   "Product4": "€420", "Product5": "€420", "Product6": "€420"}

# 第二列数据
with col[1]:
    st.header("Column 2")
    st.write("This is some content in column 2.")
    
    # 使用Column 2来放置三个排名栏目
    st.subheader("Sales Rank")
    for product, value in sales_rank_data.items():
        st.text(f"{product}: {value}")

    # 插入空行对其
    for _ in range(3): 
        st.text("")
    
    st.subheader("Revenue Rank")
    for product, value in revenue_rank_data.items():
        st.text(f"{product}: {value}")
        
    # 插入空行对其
    for _ in range(3): 
        st.text("")

    st.subheader("Rating Rank")
    for product, value in rating_rank_data.items():
        st.text(f"{product}: {value}")
        
    # 插入空行对其
    for _ in range(3): 
        st.text("")
