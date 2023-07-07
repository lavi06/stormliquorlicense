# import plotly.express as px  # pip install plotly-express
# import plotly.graph_objects as pxgo
import streamlit as st
import datetime
import requests, json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import base64, calendar, time
import altair as alt

import matplotlib
from pylab import title, figure, xlabel, ylabel, xticks, bar, legend, axis, savefig
from fpdf import FPDF
from pypdf import PdfMerger
import cv2



class FPDF(FPDF):
    def footer(self):
        # Go to 1.5 cm from bottom
        self.set_y(-15)
        # Select Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Print centered page number
        self.cell(0, 10, "Developed by Himanshu Goyal - Hggoyal06@gmail.com", 0, 0, 'R')


def pdf_first_page(city, month,year):

    border = 0
    pdf = FPDF(orientation = 'P', unit = 'mm', format='A4')

    pdf.add_page()
    pdf.set_xy(0, 0)
    pdf.set_font('arial', 'B', 12)
    pdf.set_margins(10,10,10)

    pdf.image('logo.png', x = 105-25, y = 10, w = 50, h = 25, type = '', link = '')

    pdf.set_font('', '', 10)

    pdf.cell(10, 50, ln = 1, border = border)


    text = """This Report is generated from publicly available data by Storm Liquor license."""
    pdf.cell(10)
    pdf.cell(0, 5, txt = text, border = border, ln = 1, align = '', fill = False, link = '')

    text = "Visit us at https://stormliquorlicense.com/"
    pdf.cell(10)
    pdf.cell(0, 5, txt = text, border = border, ln = 1, align = '', fill = False, link = '')

    pdf.cell(10,10, ln=1, border = border)

    pdf.set_font('', 'B', 12)
    pdf.cell(10,5,border = border)
    pdf.cell(0, 5, txt = f'Summary for {city} for month of {month}-{year}', border = border, ln = 1, align = 'L', fill = False, link = '')

    pdf.cell(10,5, ln=1, border = border)

    h = 748
    w = 916

    neww = 100
    newh = neww/w*h

    pdf.set_font('', 'U', 10)
    pdf.cell(10, 5,border = border)
    pdf.cell(0 , 5, txt = 'Chart 1 : Total Receipts by Type', border = border, ln = 1, align = 'L', fill = False, link = '')

    pdf.cell(10, 5,border = border, ln = 1)

    pdf.cell(10, newh,border = border)
    pdf.image('output1.png', x = pdf.x, y = pdf.y, w = neww, h = newh, type = '', link = '')

################################################

    pdf.add_page()

    pdf.cell(10)

    h = 1078
    w = 1089
    neww = 150
    newh = neww/w*h

    pdf.cell(0, 10,border = border, ln = 1)

    # pdf.cell(10, 5, border = border)
    pdf.cell(0 , 5, txt = 'Chart 2 : Top 25 Locations by Total Reciepts', border = border, ln = 1, align = 'L', fill = False, link = '')


    pdf.cell(10, 5,border = border, ln = 1)

    pdf.cell(10, newh,border = border)
    pdf.image('Top25.png', x = pdf.x, y = pdf.y, w = neww, h = newh, type = '', link = '')

    pdf.output('FirstPage.pdf', 'F')


def create_plots(df):

    ##########################################
    ##############Total Reciepts##############
    ##########################################

    LiquorReceipts = sum(pd.to_numeric(df["Liquor Reciepts"]))
    WineReciepts   = sum(pd.to_numeric(df["Wine Reciepts"]))
    BeerReciepts   = sum(pd.to_numeric(df["Beer Reciepts"]))
    CoverChargeReciepts = sum(pd.to_numeric(df["Cover Charge Reciepts"]))
    TotalReciepts = sum(pd.to_numeric(df["Total Reciepts"]))

    print("LiquorReceipts:", LiquorReceipts)
    print("WineReciepts:", WineReciepts)
    print("BeerReciepts:", BeerReciepts)
    print("CoverChargeReciepts:", CoverChargeReciepts)
    print("TotalReciepts:", TotalReciepts)


    fig, ax = plt.subplots(figsize =(8, 8))

    ax.bar(["Liquor Receipts","Wine Reciepts","Beer Reciepts","Cover Charge Reciepts","Total Reciepts"], [LiquorReceipts, WineReciepts, BeerReciepts, CoverChargeReciepts, TotalReciepts])
    ax.invert_xaxis()

    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    for i in ax.patches:
        # plt.text(i.get_x()+ 0.5, i.get_height() + 1000000, "$ {:,.2f}".format(i.get_height()), fontsize = 8, fontweight ='bold', color ='grey', rotation = 90)
        plt.text(i.get_x()+ 0.5, i.get_height(), "  $ {:,.2f}".format(i.get_height()), fontsize = 8, fontweight ='bold', color ='grey', rotation = 90)

    ax.grid(b = True, color ='grey', linestyle ='-.', linewidth = 0.5, alpha = 0.2)

    plt.yticks(fontsize = 10)
    plt.xticks(rotation = 90, fontsize = 8)
    plt.savefig("output1", facecolor='w', bbox_inches="tight", pad_inches=0.3, transparent=True) 

    ##########################################
    #######Top 25 Locations by Reciepts#######
    ##########################################

    total_chart = df[["Location Name","Total Reciepts"]].head(25)

    fig, ax = plt.subplots(figsize =(8, 8))
    fig.set_size_inches(12, 8)

    ax.bar(total_chart["Location Name"], total_chart["Total Reciepts"])

    for i in ax.patches:

        # plt.text( i.get_x() + 0.2, i.get_height() + 10000, "$ {:,.2f}".format(i.get_height()), fontsize = 8, fontweight ='bold', color ='grey', rotation = 90)
        plt.text( i.get_x() + 0.2, i.get_height(), "  $ {:,.2f}".format(i.get_height()), fontsize = 8, fontweight ='bold', color ='grey', rotation = 90)

    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.ylabel('Location Name', fontsize=10)
    plt.xlabel('Total Reciepts', fontsize=10)
    plt.title('Top 25 Locations by Total Reciepts')

    plt.yticks(fontsize = 10)
    plt.xticks(rotation = 90, fontsize = 8)
    plt.savefig("Top25", facecolor='w', bbox_inches="tight", pad_inches=0.3, transparent=True) 



# def create_pdf(df, city, month,year):
#     ########## Create PDF

#     create_plots(df)
#     pdf_first_page(city, month,year)

#     pp = PdfPages("Data.pdf")

#     n = 50
#     list_df = [df[i:i+n] for i in range(0,len(df),n)]

#     for df in list_df[0:5]:

#         print("Running")

#         fig, ax = plt.subplots(figsize=(12,12),squeeze=True)

#         ax.axis('tight')
#         ax.axis('off')

#         the_table = ax.table(cellText = df.values , colLabels = df.columns, loc='center', cellLoc='center')
#         the_table.auto_set_font_size(False)
#         the_table.set_fontsize(5)
#         the_table.auto_set_column_width(col=list(range(len(df.columns))))

#         pp.savefig(fig, bbox_inches='tight')

#     pp.close()

#     merger = PdfMerger()
#     for pdf in ["FirstPage.pdf", "Data.pdf"]:
#         merger.append(pdf)

#     merger.write("Final.pdf")
#     merger.close()

    # with open("foo.pdf", "rb") as pdf_file:
    #     encoded_string = pdf_file.read()
    
    # return encoded_string


# df = pd.read_excel("Excel.xlsx")
# create_pdf(df, "Dallas", "2", "2023")
# input("----")

###################################

headers = {
    'Accept': 'application/json',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Pragma': 'no-cache',
    'Referer': 'https://data.texas.gov/dataset/Mixed-Beverage-Gross-Receipts/naix-2893/explore/query/SELECT%0A%20%20%60taxpayer_number%60%2C%0A%20%20%60taxpayer_name%60%2C%0A%20%20%60taxpayer_address%60%2C%0A%20%20%60taxpayer_city%60%2C%0A%20%20%60taxpayer_state%60%2C%0A%20%20%60taxpayer_zip%60%2C%0A%20%20%60taxpayer_county%60%2C%0A%20%20%60location_number%60%2C%0A%20%20%60location_name%60%2C%0A%20%20%60location_address%60%2C%0A%20%20%60location_city%60%2C%0A%20%20%60location_state%60%2C%0A%20%20%60location_zip%60%2C%0A%20%20%60location_county%60%2C%0A%20%20%60inside_outside_city_limits_code_y_n%60%2C%0A%20%20%60tabc_permit_number%60%2C%0A%20%20%60responsibility_begin_date_yyyymmdd%60%2C%0A%20%20%60responsibility_end_date_yyyymmdd%60%2C%0A%20%20%60obligation_end_date_yyyymmdd%60%2C%0A%20%20%60liquor_receipts%60%2C%0A%20%20%60wine_receipts%60%2C%0A%20%20%60beer_receipts%60%2C%0A%20%20%60cover_charge_receipts%60%2C%0A%20%20%60total_receipts%60/page/filter',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'X-App-Token': '',
    'X-CSRF-Token': 'fsUbl73ct9odSU6l8Rr7DgUtU56TGzTH4NuG9mcggCctHJQCyvpEHwxBzGbRswfuDFncyHt2FDCJIua0w9s6/w==',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}
###################################


# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Texas Beverage Reciepts", page_icon=":bar_chart:", layout="wide")

##############################
# st.title("Production Summary ")
# st.markdown("##")
##############################


def fetch_cities():

    params = {  
                "$select": "DISTINCT(`taxpayer_city`)",
                "$order": "`taxpayer_city` ASC",
                "$limit": "10000",
                "$where": '`taxpayer_state` = "TX"'
                }

    response = requests.get('https://data.texas.gov/resource/naix-2893.json',
        params = params,
        headers=headers
    )

    data = json.loads(response.content)

    data = (response.json())

    cities = []
    for each in data:
        cities.append(each["taxpayer_city_1"])

    return cities



def fetch_df():

    city  = st.session_state.CityBox
    month = st.session_state.MonthBox
    year  = st.session_state.YearBox


    num_days = calendar.monthrange(year, month)[1]


    query = f'`taxpayer_state` = "TX" AND `location_city` = "{city}" AND ( '
    for i in range(1,num_days+1):
        if i == 1:
            query += f'`obligation_end_date_yyyymmdd` = "{year}-{month}-{i}T00:00:00.000"'

        else:
            query += f' OR `obligation_end_date_yyyymmdd` = "{year}-{month}-{i}T00:00:00.000"'

    query += " )"


    params = {  
            "$select": """
                          `location_name`,
                          `location_address`,
                          `location_zip`,
                          `tabc_permit_number`,
                          `obligation_end_date_yyyymmdd`,
                          `liquor_receipts`,
                          `wine_receipts`,
                          `beer_receipts`,
                          `cover_charge_receipts`,
                          `total_receipts`
                        """,

            "$limit": "10000000",
            "$where": query
            }


    response = requests.get('https://data.texas.gov/resource/naix-2893.json',
        params = params,
        headers= headers
    )

    data = json.loads(response.content)
    data = (response.json())
    df = pd.json_normalize(data)

    if len(df.index) > 0:
        df['obligation_end_date_yyyymmdd'] = pd.to_datetime(df['obligation_end_date_yyyymmdd'])

        df["year"]  = df["obligation_end_date_yyyymmdd"].dt.year
        df["month"] = df["obligation_end_date_yyyymmdd"].dt.month 

        df = df[(df["year"] == year) & (df["month"] == month)]

        df["total_receipts"] = pd.to_numeric(df["total_receipts"])

        df = df.sort_values(by=['total_receipts'], ascending=False)

        df = df.reset_index()
        df = df.drop(columns = ["index","year","month","obligation_end_date_yyyymmdd"])
        df = df.reset_index()
        df.index = np.arange(1, len(df) + 1)

    else:
        df = pd.DataFrame([], columns = ["index","location_name","location_address","location_zip","tabc_permit_number","liquor_receipts","wine_receipts","beer_receipts","cover_charge_receipts","total_receipt"])

    cols = ["index", "Location Name", "Location Address", "Location Zip","TABC Permit Num", "Liquor Reciepts", "Wine Reciepts","Beer Reciepts", "Cover Charge Reciepts", "Total Reciepts"]
    df.columns = cols

    return df, month, year



if "unique_cities" not in st.session_state:
    # unique_cities = fetch_cities()
    st.session_state["unique_cities"] = fetch_cities()


# ---- SIDEBAR ----

st.sidebar.header("Please Filter Here:")

city  = st.sidebar.selectbox("Select the City:" , options = ['Select'] + st.session_state["unique_cities"], key="CityBox")

year = st.sidebar.selectbox("Select the Year:"  , options = ['Select'] + list(reversed(list(range(2000,datetime.date.today().year+1)))), key="YearBox")


if year == datetime.date.today().year:
    monthoptions = list(range(1,datetime.date.today().month + 1))
else:
    monthoptions = list(range(1,13))

month = st.sidebar.selectbox("Select the Month:", options = ['Select'] + monthoptions, key="MonthBox")


if city == "Select" or month == "Select" or year == "Select":
    fetch = st.sidebar.button("Fetch Data", key="Fetch", on_click = None, disabled = True)
else:
    fetch = st.sidebar.button("Fetch Data", key="Fetch", on_click = fetch_df, disabled = False)


# @st.cache
def create_pdf(df, city, month,year):
    ########## Create PDF
    print("Running Create PDF")

    create_plots(df)
    pdf_first_page(city, month,year)

    pp = PdfPages("Data.pdf")

    n = 50

    list_df = [df[i:i+n] for i in range(0,len(df),n)]


    for i,df in enumerate(list_df,1):

        print(f"Page {i}..")
        fig, ax = plt.subplots(figsize=(12,12),squeeze=True)

        ax.axis('tight')
        ax.axis('off')

        the_table = ax.table(cellText=df.values , colLabels = df.columns, loc='center', cellLoc='center')
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(5)
        the_table.auto_set_column_width(col=list(range(len(df.columns))))

        pp.savefig(fig, bbox_inches='tight')

    pp.close()

    merger = PdfMerger()
    for pdf in ["FirstPage.pdf", "Data.pdf"]:
        merger.append(pdf)

    merger.write("Final.pdf")
    merger.close()

    with open("Final.pdf", "rb") as pdf_file:
        encoded_string = pdf_file.read()
    
    return encoded_string


# df = pd.read_excel("Excel.xlsx")
# create_pdf(df)
# input("----")


def create_charts():

    #############################
    # TOP KPI's
    #############################

    if len(df.index) > 0:
        total_records  = len(df.index)
        total_records  = '{:,}'.format(total_records)

        total_sales    = pd.to_numeric(df["Total Reciepts"]).sum()
        total_sales    = '{:,}'.format(total_sales)
    else:
        total_records = 0
        total_sales = 0


    left_column, middle_column, right_column = st.columns(3)

    with left_column:
        st.subheader("Month-Year:")
        st.subheader(f"{month}-{year}")

    with middle_column:
        st.subheader("Total Records:")
        st.subheader(f"{total_records}")

    with right_column:
        st.subheader("Total Reciepts:")
        st.subheader(f"{total_sales}")


    st.write(df.drop(columns = ["index"]))

    if len(df.index) > 0:

        csv = create_pdf(df, city, month, year)

        st.download_button("Export Data", csv, f"{city}-{year}-{month}.pdf", mime='application/octet-stream', key='download-csv')


    if len(df.index) > 0:
        total_chart = df[["Location Name","Total Reciepts"]].head(25)

        st.write(alt.Chart(total_chart, title = "Top 25 Location by Revenue").mark_bar().encode(
            x = alt.X('Location Name' , sort=None, title = "Location Name"),
            y = alt.Y('Total Reciepts', title = "Total Reciepts"),
        ))



if fetch:

    df, month, year = fetch_df()

    create_charts()



# # ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}

            footer {
                visibility: visible;
                }
            footer:after{

                diplay:block;
                content:"Developed by @Himanshu Goyal : hggoyal06@gmail.com";
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                color: white;
                text-align: right;
                padding:5px;
                padding-right: 100px

            }

            header {visibility: hidden;}
            </style>
            """


st.markdown( hide_st_style , unsafe_allow_html=True)
