import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader as web
import numpy as np
import mechanize



def getcurrentquote_us(symbol):
    br= mechanize.Browser()
    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    url='https://finance.yahoo.com/quote/' + symbol + '?p='+ symbol
    html = br.open(url)
    html = html.read()
    html = str(html)
    loc1 = html.find('Fz(36px)')
    html = html[loc1:]
    loc1 = html.find('>')
    html = html[loc1:]
    loc2 = html.find('<')
    price = html[1:loc2]
    return price



def getdata_old(symbol, settings):
    '''
    symbol is one particular symbol
    start_date is the beginning date to fetch data
    end_date is the last date to fetch data

    ret calculates the return for one day
    std_roll calculates the 10 day rolling standard deviation for use in position sizing

    '''
    #get infor from settings
    start_date=settings['initial_date']
    end_date=settings['end_date']
    std_roll_n=settings['std_roll_n']

    #get data

    df = web.DataReader(symbol, 'yahoo', start_date, end_date)


#    df = web.get_data_yahoo(symbol)
    df = df.rename(columns={'Adj Close': 'price'})  # rename to price

    df=df.dropna()

    #create some calculations
    df['ret'] = df.price.pct_change(1)
    df['std_roll'] = df['ret'].rolling(std_roll_n).std()
    df['randNumCol'] = np.random.randint(1,100, size=len(df))
    df['randNumCol'] = df['randNumCol']/10000000
    df['price']=df['price']+df['randNumCol']
    del df['randNumCol']
#    df.drop(['randNumCol'])

 #   print df
    #return the data
    return df


def getdata(symbol, settings):
#    symbol=symbol[0]
    TIINGO_API_KEY='f2af7bd8c35ac71ddb2c2d92f69ba4b762864f4a'

    start_date=settings['initial_date']
    end_date=settings['end_date']
    std_roll_n=settings['std_roll_n']

#    print (start_date)
#    print (end_date)

    df = web.get_data_tiingo(symbol, start=start_date, end=end_date, retry_count=3, pause=0.1,
                 timeout=30, session=None, freq=None, api_key=TIINGO_API_KEY)

    df=df.reset_index() #reset the default index based on symbol and date
    df['date'] = df['date'].dt.date #remove the timestamp for EOD data
    df['date'] = pd.to_datetime(df['date'])
    df=df.set_index('date') #set the new index to date
    df = df.rename(columns={'adjClose': 'price'})  # rename to price
    df=df.dropna()
    del df['symbol']
    del df['close']
    del df['divCash']
    del df['high']
    del df['low']
    del df['open']
    del df['volume']
    del df['splitFactor']

    #add current day and price if livetrading
    if  settings['livetrading'] == 'True':
        price=getcurrentquote_us(symbol)
        df.loc[end_date]=[price, price, price, price, 0] #adds a flat price and 0 volume
        df['price'] = df['price'].astype(float) #now convert columns back to floats/int
        df['adjHigh'] = df['adjHigh'].astype(float)
        df['adjLow'] = df['adjLow'].astype(float)
        df['adjOpen'] = df['adjOpen'].astype(float)
        df['adjVolume'] = df['adjVolume'].astype(int)

    #create some calculations
    df['ret'] = df.price.pct_change(1)
    df['std_roll'] = df['ret'].rolling(std_roll_n).std()
    df['randNumCol'] = np.random.randint(1,100, size=len(df))
    df['randNumCol'] = df['randNumCol']/100000
    df['price']=df['price']+df['randNumCol']
    del df['randNumCol']

    return df
