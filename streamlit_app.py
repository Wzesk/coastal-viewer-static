import altair as alt
import pandas as pd
import streamlit as st
import leafmap.foliumap as leafmap
import geopandas as gpd
from littoral import db_interaction as dbi
g_interventions = dbi.GSheetConnection('16tbbaV_klfB8ZfuwMMJrLuTxhP2W_cPvyYmpDq3ba_s','interventions')

# Show the page title and description.
st.set_page_config(page_title="Shoreline Interevention Explorer",layout="wide")

# optional title
title = False
if title:
    st.title("Shoreline Interevention Explorer")
    st.write(
        """
        Explore the impact of human activities on the coastal environment.
        """
    )

# interactions 
interactions = st.container(border=False)
# data views
viewer = st.container(border=False)

use_tabs = False
if use_tabs:
    ##setting up tab layout
    tab1, tab2, tab3 = viewer.tabs(["Table", "Timeline","Map"])
    map_height = 500
    chart_height = 320
else: 
    col = viewer.columns((4, 6), gap='medium')
    tab1 = col[0]
    tab2 = st.container(border=False)
    tab3 = col[1]
    map_height = 400
    chart_height = 200

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = g_interventions.get_sheet_pandas()
    return df


df = load_data()

# Show a multiselect widget with the genres using `st.multiselect`.
types = interactions.multiselect(
    "Type",
    df.Type.unique(),
    default=["Extension"],
)

# Show a slider widget with the years using `st.slider`.
years = interactions.slider("Date", 2010, 2024, (2010, 2024))

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[(df["Type"].isin(types)) & (df["Date"].between(years[0], years[1]))]
df_filtered = df_filtered.sort_values(by="Date", ascending=False)

#remove the lat long and number columnns from the dataframe
df_abridged = df_filtered.drop(columns=["Latitude", "Longitude", "Number"])


# Display the data as a table using `st.dataframe`.
tab1.dataframe(
    df_abridged,
    use_container_width=True,
    column_config={"Date": st.column_config.TextColumn("Date")},
)

# see the extent of projects by year
df_chart = df_filtered.groupby(["Area_sqm", "Date"], as_index=False).sum()
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("Date:N", title="Year"),
        y=alt.Y("Area_sqm:Q", title="Total Area (sqm)"),
        color="Type:N",
    )
    .properties(height=chart_height)
)
tab2.altair_chart(chart, use_container_width=True)

with tab3:
    islands = df_filtered

    #get the average value of the lat and long
    ave_lat = islands["Latitude"].mean()
    ave_long = islands["Longitude"].mean()
    m = leafmap.Map(center=[ave_lat, ave_long], draw_export=True, zoom=7)

    gdf = gpd.read_file("data/countour/20160103T053712_20160103T053706_T43NCE_wsl_world_coordinates.geojson")#"data/test_proj_world_coordinates.geojson")

    m.add_gdf(gdf, layer_name="shorelines", zoom_to_layer=False)

    m.add_points_from_xy(islands, x="Longitude", y="Latitude")

    m.add_basemap("SATELLITE")
    m.to_streamlit(height=map_height)
