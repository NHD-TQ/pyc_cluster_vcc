import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from matplotlib.gridspec import GridSpec
import seaborn as sns
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler as ss
from sklearn.preprocessing import StandardScaler

def process_rfm(path_data):
    df = pd.read_excel(path_data)
    Latest_date = dt.datetime(2024,6,8)
    df['CUSTOMER_PHONE'] = df['CUSTOMER_PHONE'].astype(str).apply(lambda x: '0' + x.split('.')[0])
    df['CREATED_DATE'] = pd.to_datetime(df['CREATED_DATE'])
    RFM = df.groupby('CONTRACT_CODE').agg({
    'CREATED_DATE': lambda x :(Latest_date - x.max()).days,
    'GOODS_CODE': ', '.join,  # Nối các mã hàng hoá thành chuỗi
    'GOODS_NAME': ', '.join,  
    'CUSTOMER_ID': 'first',  
    'CUSTOMER_PHONE': 'first', 
    'CUSTOMER_NAME': 'first',  
    'CUSTOMER_ADDRESS': 'first',  
    'CONTRACT_AMOUNT': 'first'
    }).reset_index()

    RFM_v1 = RFM.groupby('CUSTOMER_ID').agg({
    'CREATED_DATE': lambda x :(x.min()),  # Lấy ngày đầu tiên (vì tất cả ngày giống nhau)
    'GOODS_CODE': ', '.join,  
    'GOODS_NAME': ', '.join,  
    'CONTRACT_CODE': 'count',
    'CUSTOMER_PHONE': 'first',
    'CUSTOMER_NAME': 'first',  
    'CUSTOMER_ADDRESS': 'first',  
    'CONTRACT_AMOUNT': 'sum'  
    }).reset_index()

    RFM_v1 = RFM_v1[['CUSTOMER_ID', 'CUSTOMER_PHONE', 'CREATED_DATE', 'CONTRACT_CODE', 'CONTRACT_AMOUNT']]

    RFM_v1.rename(columns = {'CREATED_DATE' : 'Recency',
                          'CONTRACT_CODE' : "Frequency",
                          'CONTRACT_AMOUNT' : "Monetary"}, inplace = True)
    
    RFM_v1.rename(columns = {'CUSTOMER_ID' : 'CustomerID',
                          },inplace = True)
    df_rfm = RFM_v1
    df_rfm['Monetary'] *= 2 # Moneytory with 2
    return df_rfm

# First will focus on the negativ and zero before the transformation.
def right_treat(var):
    if var <= 0:
        return 1
    else:
        return var

def cluster_kmean(RFM_data):
    RFM_data['Recency'] = RFM_data['Recency'].apply(lambda x : right_treat(x))
    RFM_data['Monetary'] = RFM_data['Monetary'].apply(lambda x : right_treat(x))
    log_RFM_data = RFM_data[['Recency','Frequency','Monetary']].apply(np.log,axis = 1).round(4)
    ss = StandardScaler()
    Scaled_RFM_data = ss.fit_transform(log_RFM_data)
    Scaled_RFM_data = pd.DataFrame(Scaled_RFM_data,columns=log_RFM_data.columns,index=log_RFM_data.index)
    mean = ss.mean_
    scale = ss.scale_
    KM_clust = KMeans(n_clusters= 4, init = 'k-means++',max_iter = 1000, random_state=42)
    KM_clust.fit(Scaled_RFM_data)

    # Mapping on the data
    RFM_data['Cluster'] = KM_clust.labels_
    RFM_data['Cluster'] = 'Cluster' + RFM_data['Cluster'].astype(str)

    return mean, scale, RFM_data, KM_clust, Scaled_RFM_data
