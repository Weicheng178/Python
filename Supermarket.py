import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from wordcloud import WordCloud
import datetime 
from io import BytesIO


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

st.divider()

# 以下是侧边栏小部件区域

# 城市多选小部件
option1 = st.sidebar.multiselect(
    'City',
    ['Yangon', 'Naypyitaw', 'Mandalay'],
    ['Yangon', 'Naypyitaw', 'Mandalay'])

# 时间小部件
first_day = datetime.date(2019, 1, 1)
last_day = datetime.date(2019, 3, 31)
date_value = st.sidebar.date_input( 
    "Date",
    (first_day, last_day),
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
#--------------------zc Part-------------------------------------------

col = st.columns([3, 1])
# 第一列数据
with col[0]:
    # 在第一列中创建三个子容器
    col_sub = st.columns([2, 2.2, 1])

    # 处理筛选栏部分数据
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
        
#----------------------zc Part---------------------------------------
    # 分隔符
    st.divider()
    
    # 折线图
    df = load_data()
    df['Date'] = pd.to_datetime(df['Date'])
    
    grouped_sales = df.groupby([df['Date'].dt.to_period('M'), 'Customer type'])['Total'].sum().unstack()
    grouped_sales = grouped_sales.fillna(0) 
    grouped_sales.index = grouped_sales.index.to_timestamp()
    
    st.header('Sales Trend Visualization')
    
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


    # 分隔符
    st.divider()

    # 表格打印
    st.header('Customer segmentation')
    
    options = ["Total Customer",'Sensitive Customer','Risk Customer']
    customer_type = st.radio("Choose a Customer Type", options)
    
    df = load_data()
    filtered_df = filter_customers(customer_type, df)
    
    st.dataframe(filtered_df)
    
    # 分隔符
    st.divider()
    
    
    #词云显示
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(df['Product line']))
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout(pad=0)
    
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    st.image(buf, use_column_width=True)
    



#----------------------zc Part---------------------------------------
# 第二列数据
with col[1]:
    
    # 使用Column 2来放置三个排名栏目
    st.subheader("Sales Rank")
    # 处理筛选栏部分数据
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
        

    # 插入空行对其
    st.divider()
    
    st.subheader("Revenue Rank")
    # 处理筛选栏部分数据
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
        
        
    # 插入空行对其
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
