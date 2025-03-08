import pandas as pd
import shapely.wkt
import geopandas as gpd
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from gspread_dataframe import get_as_dataframe, set_with_dataframe

class GSheetConnection:
    def __init__(self,gsheetkey,sheet_name):
        self.gsheetkey = gsheetkey
        self.sheet_name = sheet_name
        # self.gc = gspread.service_account(filename='littoral-442716-b40e7c7bd861.json')
        # self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # self.creds = ServiceAccountCredentials.from_json_keyfile_name('littoral-442716-b40e7c7bd861.json', self.scope)
   
    def get_sheet_pandas(self):
        str_key = self.gsheetkey
        url=f'https://docs.google.com/spreadsheet/ccc?key={str_key}&output=xlsx'
        df = pd.read_excel(url,sheet_name=self.sheet_name)
        return df
    
    # def get_sheet_df(self):
    #     sh = self.gc.open_by_key(self.gsheetkey)
    #     worksheet = sh.worksheet(self.sheet_name)
    #     df = get_as_dataframe(worksheet)
    #     return df
    
    # def write_sheet_df(self,df):
    #     sh = self.gc.open_by_key(self.gsheetkey)
    #     worksheet = sh.worksheet(self.sheet_name)
    #     set_with_dataframe(worksheet , df)
    #     df2 = get_as_dataframe(worksheet)
    #     return df2


def load_islands():
    df = pd.read_csv('data/island_data/island-polygon.csv', sep='\t')
    gdf = gpd.GeoDataFrame(df, geometry=df['WKT'].apply(shapely.wkt.loads))
    return gdf