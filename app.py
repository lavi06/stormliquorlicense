import pandas as pd  # pip install pandas openpyxl
# import plotly.express as px  # pip install plotly-express
# import plotly.graph_objects as pxgo
import streamlit as st  # pip install streamlit
import datetime
import io
import requests, json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import base64, calendar, time
import altair as alt

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

    cols = ["index", "Location Name", "Location Address", "Location Zip","TABC Permit Num", "Liquor Receipts", "Wine Reciepts","Beer Reciepts", "Cover Charge Reciepts", "Total Reciepts"]
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


def create_pdf(df):
    ########## Create PDF

    fig, ax = plt.subplots(figsize=(12,12),squeeze=True)

    ax.axis('tight')
    ax.axis('off')

    the_table = ax.table(cellText=df.values , colLabels=df.columns, loc='center', cellLoc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(5)
    the_table.auto_set_column_width(col=list(range(len(df.columns))))

    pp = PdfPages("foo.pdf")

    # pp.text(0.05,0.95,txt, transform=fig.transFigure, size=24)

    pp.savefig(fig, bbox_inches='tight')
    pp.close()

    with open("foo.pdf", "rb") as pdf_file:
        encoded_string = pdf_file.read()
    
    return encoded_string



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
        csv = create_pdf(df)

        st.download_button("Export Data", csv, f"{city}-{year}-{month}.pdf", mime='application/octet-stream', key='download-csv', on_click = create_charts)

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
