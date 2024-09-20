
import os
import re
import glob
import pandas as pd
import numpy as np
import pdfplumber
import itertools
from datetime import datetime, timedelta


def datecoll(startday, endday):
    
    x=list()
    count=0
    
    while datetime.strptime(endday,'%Y-%m-%d')>=(datetime.strptime(startday,'%Y-%m-%d')+timedelta(days=count)):
        
        DD=(datetime.strptime(startday,'%Y-%m-%d')+timedelta(days=count)).date()
        x.append([DD.strftime("%Y-%m-%d"), DD.strftime("%Y%m%d"), DD.strftime("%m%d"), DD.strftime("%Y-%m"), DD])
        count=count+1
    
    return x


def date_adj(current_date):
    endday = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')

    if current_date.weekday() == 0:
        startday = (current_date - timedelta(days=3)).strftime('%Y-%m-%d')
    else:
        startday = endday
    
    return startday, endday


def transform_pdf_to_text(pdf_path):

    with pdfplumber.open(pdf_path) as pdf:
        
        raw_text  = ''
        
        for p in range(len(pdf.pages)):

            The_page = pdf.pages[p] 
            raw = The_page.extract_text(y_tolerance=1)
            raw = raw if type(raw) == str else '' # 排除none type
            
            raw_text += raw + '\n' # 避免資料剛好因分頁被合併再一起
            
    return raw_text


def str_clean_f(server_list: list):

    result = list(map(lambda x: re.sub(r'_\d{8}.pdf', '', x), server_list))

    return result


#######
class LP_statement_task():

    def __init__(self, nas_path, statement_dict):
        
        # set tdday
        current_date = datetime.now()
        startday, endday = date_adj(current_date)
        self.TDday = datecoll(startday, endday)
        
        # nas path 
        self.nas_path = nas_path
       
        # get server for each blocks
        self.OP_servers = str_clean_f(statement_dict['OP_servers'])
        self.JCS_servers = str_clean_f(statement_dict['JCS_servers'])
        self.CDET_servers = str_clean_f(statement_dict['CDET_servers'])
        self.EDRT_servers = str_clean_f(statement_dict['EDRT_servers'])

        # all servers
        self.all_servers = set(self.OP_servers + self.JCS_servers + self.CDET_servers + self.EDRT_servers)


    # finding symbol with relative position from specific word!
    @staticmethod
    def symbol_assign(df, data, split_word):

        for idx, t in enumerate(data):

            if re.match(split_word, t):
                The_Symbol = data[idx-1]
        
                print(idx, The_Symbol)

                df.symbol.iloc[idx:] = The_Symbol    

        return df


    def open_positions_f(self, open_positions):

        pattern = [r'(^.*) 2022.* ', r'([0-9]{4}-[0-9]{2}-[0-9]{2})', r'(\-?\d*\.\d*)']
        open_positions_data = list(map(lambda x:[re.findall(pat, x) for pat in pattern], open_positions))
        open_positions_data = [list(itertools.chain(*i)) for i in open_positions_data]  ### flatten the nested list
        df_open_positions = pd.DataFrame(columns=['Core Symbol', 'Value Date', 'CCY1 Quantity', 'CCY2 Quantity', 'VWAP', 'Unrealized P&L'], data=open_positions_data)

        return df_open_positions


    def Journals_and_Cash_Sweeps_f(self, Journals_and_Cash_Sweeps):
        pattern = [r'^\d{6}', r'2022.*:[0-9]{2}', r':[0-9]{2} (\w+ \w+)', r'\w+ \w+ ([A-Z]{3})', r'(\-?\d*\.\d*)', r'\-?\d*\.\d* (.*)']
        Journals_and_Cash_Sweeps_data = list(map(lambda x: [re.findall(pat, x) for pat in pattern], Journals_and_Cash_Sweeps))
        Journals_and_Cash_Sweeps_data = [list(itertools.chain(*i)) for i in Journals_and_Cash_Sweeps_data]  ### flatten the nested list
        df_Journals_and_Cash_Sweeps = pd.DataFrame(columns=['Transaction ID', 'Date/Time', 'Transaction Type', 'Currency', 'Amount', 'Comment'], 
                                                   data=Journals_and_Cash_Sweeps_data)

        return df_Journals_and_Cash_Sweeps


    def Current_Day_Executed_Trades_f(self, Current_Day_Executed_Trades):
        
        pattern = [r'^(\d{8,9}).*(-\d.\d*).*(\w{3})$']
        Current_Day_Executed_Trades_data = list(map(lambda x:[re.findall(pat, x) for pat in pattern], Current_Day_Executed_Trades))
        Current_Day_Executed_Trades_data = [list(i[0][0]) if len(i[0])>0 else [np.nan] for i in Current_Day_Executed_Trades_data] ### 取資料出來

        df_Current_Day_Executed_Trades_raw_data = pd.DataFrame(columns=['Execution ID', 'Commission', 'CCY'], data=Current_Day_Executed_Trades_data) \
                                                    .assign(symbol='')

        df_Current_Day_Executed_Trades = self.symbol_assign(df_Current_Day_Executed_Trades_raw_data, 
                                                            Current_Day_Executed_Trades, 
                                                            '^Execution.*') \
                                             .query('~`Execution ID`.isna()') \
                                             .reset_index(drop=True)  

        return df_Current_Day_Executed_Trades


    def End_of_Day_Roll_Transactions_f(self, End_of_Day_Roll_Transactions):
        
        pattern = [r'^(\d{8,9})',  r'^\d{8,9} ([0-9]{4}-[0-9]{2}-[0-9]{2})',  r'(\-?\d*\.\d*)', r'([0-9]{4}-[0-9]{2}-[0-9]{2})$'] #, r'([0-9]{4}-[0-9]{2}-[0-9]{2})', r'(\-?\d*\.\d*)'
        End_of_Day_Roll_Transactions_data = list(map(lambda x:[re.findall(pat, x) for pat in pattern], End_of_Day_Roll_Transactions))
        End_of_Day_Roll_Transactions_data = [list(itertools.chain(*i)) for i in End_of_Day_Roll_Transactions_data]           ### flatten the nested list
        cols = ['OrderID', 'Trade Date', 'CCY1 Quantity', 'CCY2 Quantity', 'Price', 'Value Date']
        End_of_Day_Roll_Transactions_data = [i if len(i) == len(cols)  else [np.nan] for i in End_of_Day_Roll_Transactions_data]
        df_End_of_Day_Roll_Transactions = pd.DataFrame(columns=cols, data=End_of_Day_Roll_Transactions_data) \
                                            .assign(symbol='')        

        df_End_of_Day_Roll_Transactions = self.symbol_assign(df_End_of_Day_Roll_Transactions, 
                                                             End_of_Day_Roll_Transactions, 
                                                             '^OrderID.*') \
                                                    .query('~(OrderID.isna()|OrderID ==".")') \
                                                    .reset_index(drop=True)
        
        return df_End_of_Day_Roll_Transactions


    def main(self):
        
        output_file_path = []

        ### Concat all strings
        for k in range(len(self.TDday)): # k=0
            
            print(self.TDday[k][0])
            df_open_positions= pd.DataFrame()
            df_Journals_and_Cash_Sweeps= pd.DataFrame()
            df_Current_Day_Executed_Trades= pd.DataFrame()
            df_End_of_Day_Roll_Transactions = pd.DataFrame()

            for server in self.all_servers: # server = 'IV_SVG'
                print(f'========================={server}=========================')
                pdf_path = f'{self.nas_path}/LP PNL/奇怪的PDF存放區/{self.TDday[k][1][:4]}/{server}_{self.TDday[k][1]}.pdf'
                raw_all = transform_pdf_to_text(pdf_path)

                ### Seperate with title name
                separators_list = ['Open Positions', 'Journals and Cash Sweeps', 'Current Day Executed Trades', 'End of Day Roll Transactions']
                seperators_regex = '|'.join(separators_list)

                raw_all = re.sub(',', '', raw_all) ### 逗號影響判斷&抓取
                split_data = list(filter(None, re.split(seperators_regex, raw_all)))

                ### Remove unneccessary elements and turn each in dataframe
                split_data_filtered = split_data[1:]
                

                # open position
                try:
                    if server in self.OP_servers:
                        open_positions = split_data_filtered[0].split('\n')[2:-1]
                        df_op = self.open_positions_f(open_positions)
                        df_open_positions = pd.concat([df_open_positions, df_op], ignore_index=True)
                except:
                    print(server, ' has no open position data!!')
                    pass

                # Journals and Cash Sweeps
                try:
                    if server in self.JCS_servers:
                        Journals_and_Cash_Sweeps = split_data_filtered[1].split('\n')[2:-1]
                        df_JCS = self.Journals_and_Cash_Sweeps_f(Journals_and_Cash_Sweeps)
                        df_Journals_and_Cash_Sweeps = pd.concat([df_Journals_and_Cash_Sweeps, df_JCS], ignore_index=True)
                except:
                    print(server, ' has no Journals and Cash Sweeps data!!')
                    pass

                # Current Day Executed Trades
                try:
                    if server in self.CDET_servers:
                        Current_Day_Executed_Trades = split_data_filtered[2].split('\n')
                        df_CDET = self.Current_Day_Executed_Trades_f(Current_Day_Executed_Trades) \
                                      .assign(db=server,
                                              date = self.TDday[k][0]) \
                                      .filter(items=['db', 'symbol', 'Execution ID', 'Commission', 'CCY', 'date'])
                        df_Current_Day_Executed_Trades = pd.concat([df_Current_Day_Executed_Trades, df_CDET], ignore_index=True)
                except:
                    print(server, ' has no Current Day Executed Trades data!!')
                    pass
                
                ### End of Day Roll Transactions
                try:
                    if server in self.EDRT_servers:         
                        End_of_Day_Roll_Transactions = split_data_filtered[3].split('\n')
                        df_EDRT = self.End_of_Day_Roll_Transactions_f(End_of_Day_Roll_Transactions) \
                                    .assign(pdf=server) \
                                    .filter(items=['pdf', 'symbol', 'OrderID', 'Trade Date', 'CCY1 Quantity', 'CCY2 Quantity', 'Price', 'Value Date'])
                        df_End_of_Day_Roll_Transactions = pd.concat([df_End_of_Day_Roll_Transactions, df_EDRT], ignore_index=True)
                except:
                    print(server, ' has no End of Day Roll Transactions data!!')
                    pass


            # 輸出檔案
            output_dataframe = {"Open_Positions": df_open_positions, 
                                "Journals_and_Cash_Sweeps": df_Journals_and_Cash_Sweeps, 
                                "Current_Day_Executed_Trades": df_Current_Day_Executed_Trades,
                                "End_of_Day_Roll_Transactions": df_End_of_Day_Roll_Transactions}

            for file_name, df in output_dataframe.items():
                
                print(file_name, df)
                
                if len(df) != 0:
                    path = f'{self.nas_path.replace("Dropbox", "")}日報文檔/Tim/{file_name}_{self.TDday[k][0]}_beta.xlsx'
                    df.to_excel(path, index=False)

                    output_file_path.append(path)
            
        return output_file_path
