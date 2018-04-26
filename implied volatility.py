from math import log,sqrt,exp,pi
from scipy.stats import norm
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt

	   
def option_price(spot,strike,t,maturity,r,q,volatility,type):
    global price
    d1=(log(spot/strike)+(r-q)*(maturity-t))/volatility/sqrt(maturity-t)+0.5*volatility*sqrt(maturity-t)
    d2=d1-volatility*sqrt(maturity-t)
    if(type=='C'):
        price=spot*exp(-q*(maturity-t))*norm.cdf(d1)-strike*exp(-r*(maturity-t))*norm.cdf(d2)
    elif(type=='P'):
        price=strike*exp(-r*(maturity-t))*norm.cdf(-d2)-spot*exp(-q*(maturity-t))*norm.cdf(-d1)
    return price

def guess_initial(spot,strike,t,maturity,r,q):
    sigmahat=sqrt(2*abs((log(spot/strike)+(r-q)*(maturity-t))/(maturity-t)))
    return sigmahat

def derivative(spot,strike,t,maturity,r,q,volatility):
    d1=(log(spot/strike)+(r-q)*(maturity-t))/volatility/sqrt(maturity-t)+0.5*volatility*sqrt(maturity-t)
    der=spot/sqrt(2*pi)*exp(-q*(maturity-t)-0.5*d1*d1)*sqrt(maturity-t)
    return der
    

#import data
reader1=pd.DataFrame(pd.read_csv('marketdata.csv'))
reader2=pd.DataFrame(pd.read_csv('instruments.csv'))
reader_merged=pd.merge(reader1,reader2,on='Symbol',how='left')
#reader_merged.to_csv('E:\\merger.csv')
#print(reader_merged)


#selection
split=pd.DataFrame((x.split() for x in reader_merged['LocalTime']),index=reader_merged.index,columns=['Date','Time'])
reader_merged=pd.merge(reader_merged,split,right_index=True,left_index=True)
#print(reader_merged)
#print(reader_merged.info())
selected=[]
selected.append(reader_merged.loc[ (reader_merged['Time']).str[:8]<'09:31:00',['Date','Time','Symbol','Bid1','Ask1','Strike','OptionType']])
selected.append(reader_merged.loc[ ((reader_merged['Time']).str[:8]<'09:32:00')&((reader_merged['Time']).str[:8]>='09:31:00'),['Date','Time','Symbol','Bid1','Ask1','Strike','OptionType']])
selected.append(reader_merged.loc[ ((reader_merged['Time']).str[:8]<'09:33:00')&((reader_merged['Time']).str[:8]>='09:32:00'),['Date','Time','Symbol','Bid1','Ask1','Strike','OptionType']])
#print(selected[2])


#calculation

tol=1e-8
nmax=100
maturity=24.0/365
t=16.0/365
r =0.04
q =0.2

writer=[]
writer.append(pd.DataFrame(columns=['Symbol','Strike','BidVolP','AskVolP','BidVolC','AskVolC']))
writer.append(pd.DataFrame(columns=['Symbol','Strike','BidVolP','AskVolP','BidVolC','AskVolC']))
writer.append(pd.DataFrame(columns=['Symbol','Strike','BidVolP','AskVolP','BidVolC','AskVolC']))

#calculate Ask 
i=0
while(i<3):
    j=0
    selected[i]=selected[i].reset_index(drop=True)
    spot_ask=selected[i].loc[selected[i]['Symbol']==510050,['Ask1']]['Ask1'].mean()    
    print(spot_ask)
    while(j<selected[i].shape[0]):
     n=1
     strike = selected[i].at[j,'Strike']
     real_price=selected[i].at[j,'Ask1']
     type=selected[i].at[j,'OptionType']
     #identify arbitrage
     if(type=='C')&(real_price<spot_ask*exp(-q*(maturity-t))-strike*exp(-r*(maturity-t)))==True or (type=='P')&(real_price>strike*exp(-r*(maturity-t)))==True:
         sigma=np.NaN
     elif(type=='C')&(real_price>spot_ask)==True or (type=='P')&(real_price<strike*exp(-r*(maturity-t))-spot_ask*exp(-q*(maturity-t)))==True:
         sigma=np.NaN
     else:
         sigma=guess_initial(spot_ask,strike,t,maturity,r,q)
         #print(sigma)
         option_value=option_price(spot_ask,strike,t,maturity,r,q,sigma,type)
         #print(spot_ask,strike,t,maturity,r,q,sigma,type)
         vega=derivative(spot_ask,strike,t,maturity,r,q,sigma)
         while((abs(option_value-real_price)>=tol) & (n<=100)):
             if(vega==0):
                 break
             increment=(option_value-real_price)/vega
             sigma=sigma-increment
             #print(sigma,vega)
             option_value=option_price(spot_ask,strike,t,maturity,r,q,sigma,type)
             vega=derivative(spot_ask,strike,t,maturity,r,q,sigma)
             n=n+1
     if(type=='C'):
         writer[i].loc[j,'AskVolC']=sigma
         writer[i].loc[j,'Strike']=strike
         writer[i].loc[j,'Symbol']=selected[i].at[j,'Symbol']
     elif(type=='P'):     
         writer[i].loc[j,'AskVolP']=sigma
         writer[i].loc[j,'Strike']=strike
         writer[i].loc[j,'Symbol']=selected[i].at[j,'Symbol']
         
     j=j+1
    i=i+1

#calculation bid
i=0
while(i<3):
    j=0
    spot_bid=selected[i].loc[selected[i]['Symbol']==510050,['Bid1']]['Bid1'].mean()
    print(spot_bid)
    while(j<selected[i].shape[0]):
     n=1
     strike = selected[i].at[j,'Strike']
     real_price=selected[i].at[j,'Bid1']
     type=selected[i].at[j,'OptionType']
     #identify arbitrage
     if(type=='C')&(real_price<spot_bid*exp(-q*(maturity-t))-strike*exp(-r*(maturity-t)))==True or (type=='P')&(real_price>strike*exp(-r*(maturity-t)))==True:
         sigma=np.NaN
     elif(type=='C')&(real_price>spot_bid)==True or (type=='P')&(real_price<strike*exp(-r*(maturity-t))-spot_bid*exp(-q*(maturity-t)))==True:
         sigma=np.NaN
     else:
         sigma=guess_initial(spot_bid,strike,t,maturity,r,q)
         #print(sigma)
         option_value=option_price(spot_bid,strike,t,maturity,r,q,sigma,type)
         vega=derivative(spot_bid,strike,t,maturity,r,q,sigma)
         #print(spot_bid,strike,t,maturity,r,q,sigma,type)
         while((abs(option_value-real_price)>=tol) & (n<=100)):
             if(vega==0):
                 break
             increment=float((option_value-real_price)/vega)
             sigma=sigma-increment
             #print(sigma,vega)
             option_value=option_price(spot_bid,strike,t,maturity,r,q,sigma,type)
             vega=derivative(spot_bid,strike,t,maturity,r,q,sigma)
             n=n+1
     if(type=='C'):
         writer[i].loc[j,'BidVolC']=sigma
     elif(type=='P'):
         writer[i].loc[j,'BidVolP']=sigma
     
     j=j+1
    i=i+1
#print(writer[2]) 


#layout table and draw plots
h=0
while(h<3):
    writer[h].drop_duplicates(['Symbol'],keep='last',inplace=True)
    #print( writer[h].loc[(writer['BidVolP']<0)|(writer['BidVolP']>100),['BidVolP']])
    first=pd.DataFrame(writer[h].drop_duplicates(['Strike'],keep='first'),columns=['Strike','BidVolP','AskVolP','BidVolC','AskVolC'])
    #print(first)
    last=pd.DataFrame(writer[h].drop_duplicates(['Strike'],keep='last'),columns=['Strike','BidVolP','AskVolP','BidVolC','AskVolC'])
    #print(last)
    first1=pd.DataFrame(first.set_index('Strike'),dtype=np.float)
    last1=pd.DataFrame(last.set_index('Strike'),dtype=np.float)
    #print(first1)
    #print(first1.info())
    #print(last1)
    writer[h]=first1.add(last1,fill_value=0)
    print(writer[h])
    writer[h].plot()
    
    plt.show()
    h=h+1

writer[0].to_csv('31.csv',na_rep='NaN')
writer[1].to_csv('32.csv',na_rep='NaN')
writer[2].to_csv('33.csv',na_rep='NaN')



