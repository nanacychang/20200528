import requests
import pandas as pd
from bs4 import BeautifulSoup

#基本資訊
url='https://www.sitca.org.tw/ROC/Industry/IN2422.aspx?txtYEAR=2020&txtMONTH=04&txtGROUPID=EUCA000537'
headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

# 觀察發現透過 id ctl00_ContentPlaceHolder1_TableClassList 可以取出 Morningstar table 資料。取出第一筆
table_content = soup.select('#ctl00_ContentPlaceHolder1_TableClassList')[0]

# 將 BeautifulSoup 解析的物件美化後交給 pandas 讀取 table，注意編碼為 UTF-8。取出第二筆
fund_df = pd.read_html(table_content.prettify(), encoding='utf-8')[1]

# 資料前處理，將不必要的列
fund_df = fund_df.drop(index=[0])
# 設置第一列為標頭
fund_df.columns = fund_df.iloc[0]
# 去除不必要列
fund_df = fund_df.drop(index=[1])
# 整理完後新設定 index
fund_df.reset_index(drop=True, inplace=True)
# NaN -> 0
fund_df = fund_df.fillna(value=0)

print('fund_df', fund_df.dtypes)

# 轉換資料型別從 object 轉為 float
fund_df['一個月'] = fund_df['一個月'].astype(float)
fund_df['三個月'] = fund_df['三個月'].astype(float)
fund_df['六個月'] = fund_df['六個月'].astype(float)
fund_df['一年'] = fund_df['一年'].astype(float)
fund_df['二年'] = fund_df['二年'].astype(float)
fund_df['三年'] = fund_df['三年'].astype(float)
fund_df['五年'] = fund_df['五年'].astype(float)
fund_df['自今年以來'] = fund_df['自今年以來'].astype(float)

print('fund_df', fund_df.dtypes)
# 前二分之一筆資料數量
half_of_row_count = len(fund_df.index) // 2

# 316 法則篩選標準，ascending True 為由小到大排序，nlargest 為取出前面 x 筆資料，// 代表取整數去掉小數（轉為整數意思）
rule_3_df = fund_df.sort_values(by=['三年'], ascending=['True']).nlargest(half_of_row_count, '三年')
rule_1_df = fund_df.sort_values(by=['一年'], ascending=['True']).nlargest(half_of_row_count, '一年')
rule_6_df = fund_df.sort_values(by=['六個月'], ascending=['True']).nlargest(half_of_row_count, '六個月')

# 取三者交集（merge 一次只能兩個 DataFrame，先前兩個取交集再和後一個取交集）
rule_31_df = pd.merge(rule_3_df, rule_1_df, how='inner')
rule_316_df = pd.merge(rule_31_df, rule_6_df, how='inner')

print('三年前 1/2')
for index, row in rule_3_df.iterrows():
    print(index, row['基金名稱'], row['三年'], row['一年'], row['六個月'])


print('一年前 1/2')
for index, row in rule_1_df.iterrows():
    print(index, row['基金名稱'], row['三年'], row['一年'], row['六個月'])

print('六個月 1/2')
for index, row in rule_6_df.iterrows():
    print(index, row['基金名稱'], row['三年'], row['一年'], row['六個月'])

print('====316 法則====\n', rule_316_df)
