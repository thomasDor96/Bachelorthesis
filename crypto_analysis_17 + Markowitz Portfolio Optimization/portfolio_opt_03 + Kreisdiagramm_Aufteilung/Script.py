#Импортирование всех необходимых библиотек

import pandas as pd #Необходима для работы с таблицами
import numpy as np #Линейная алгебра
import matplotlib.pyplot as plt #Визуализация
import quandl #Необходимо для загрузки котировок акций


#Чтение TOP500 компаний S&P
list_of_companies = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', header=0)[0]
list_of_companies=list_of_companies.drop(['SEC filings','CIK','Date first added[3][4]'],axis=1)

#Выбираем компании
chosen_companies=[]
comp_num=int(input("Введите количество компаний в портфеле - "))
for i in range(comp_num):
    kompany=str((input('Введите тикер компании {} - '.format(i+1))))
    while kompany not in list(list_of_companies['Ticker symbol']):
        kompany=str((input('Введите корректный тикер компании {} - '.format(i+1))))
    chosen_companies.append(kompany)

#Подключение к Quandl
quandl.ApiConfig.api_key='DsNzPHqf1ffR8znxL8vH' 

#Скачиваем котировки акций выбранных компаний
database = quandl.get_table('WIKI/PRICES', ticker = chosen_companies, 
                        qopts = { 'columns': ['ticker', 'date', 'adj_close'] }, 
                        date = { 'gte': '2016-12-31', 'lte': '2018-04-06' }, paginate=True)
database=database.set_index('date')
database=database.pivot(columns='ticker')
database.columns=[col[1] for col in database.columns]

# База данных по доходностям
returns_database=database.pct_change()

#Дневные и годовые доходности и ковариации
daily_returns=returns_database.mean() 
daily_cov=returns_database.cov() 
annual_returns=daily_returns*250
annual_cov=daily_cov*250

#Задаем количество портфелей
assets_num=len(chosen_companies)
portfolios_num=50000
np.random.seed(101)

#Создаем пустые списки для доходности, волатильности, весов и коэффицента Шарпа для каждого из портфелей
portfolio_returns=[]
portfolio_volatility=[]
portfolio_weights=[]
sharpe_ratio=[]

for portfolio in range(portfolios_num):
    weights=np.random.random(assets_num)
    weights /= np.sum(weights)
    port_return=np.dot(weights,annual_returns)
    port_volatility=np.sqrt(np.dot(weights.T,np.dot(annual_cov,weights)))
    sharpe=port_return/port_volatility
    sharpe_ratio.append(sharpe)
    portfolio_returns.append(port_return)
    portfolio_volatility.append(port_volatility)
    portfolio_weights.append(weights)
    
portfolio={'Доходность':portfolio_returns, 'Риск':portfolio_volatility, 'Коэффицент Шарпа':sharpe_ratio}
for counter,symbol in enumerate(chosen_companies):
    portfolio[symbol] = [Weight[counter]*100 for Weight in portfolio_weights]
    
df=pd.DataFrame(portfolio)

min_volatility=df['Риск'].min()
max_sharp=df['Коэффицент Шарпа'].max()

min_vol_port=df[df['Риск']==min_volatility]
max_sharp_port=df[df['Коэффицент Шарпа']==max_sharp]

a=input("Выберите модель оптимизации: ")
if a=='Sharpe':
    #Портфель с максимальным коэффицентом Шарпа
    print(max_sharp_port.T.round(2))
    labels=list(max_sharp_port.columns)[3:]
    data=max_sharp_port.iloc[0,3:]
    fig,ax=plt.subplots(figsize=(9,6))
    ax.pie(data,labels=labels,autopct='%1.1f%%')
    plt.axis('equal')
    plt.show()
elif a=='Volatility':
 #Портфель с минимальной волатильностью
    print(min_vol_port.T.round(2))
    labels=list(min_vol_port.columns)[3:]
    data=min_vol_port.iloc[0,3:]
    fig,ax=plt.subplots(figsize=(9,6))
    ax.pie(data,labels=labels,autopct='%1.1f%%')
    plt.axis('equal')
    plt.show()
else: print("Error")
