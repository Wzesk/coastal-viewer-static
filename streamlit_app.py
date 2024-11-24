import altair as alt
import pandas as pd
import streamlit as st
import leafmap.foliumap as leafmap
import geopandas as gpd
# import os
# os.environ["MAPTILER_KEY"] = "H2po2DoUxvE0BAWFzoa0"


# Show the page title and description.
st.set_page_config(page_title="Shoreline Interevention Explorer",layout="wide")
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
##setting up tab layout
tab1, tab2, tab3 = viewer.tabs(["Table", "Timeline","Map"])


# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/reclaimed_Islands_gt_bg.csv") 
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
    .properties(height=320)
)
tab2.altair_chart(chart, use_container_width=True)

with tab3:
    islands = df_filtered

    #get the average value of the lat and long
    ave_lat = islands["Latitude"].mean()
    ave_long = islands["Longitude"].mean()
    m = leafmap.Map(center=[ave_lat, ave_long], draw_export=True, zoom=7)

    gdf = gpd.read_file("data/test_proj_world_coordinates.geojson")

    m.add_gdf(gdf, layer_name="shorelines", zoom_to_layer=False)

    m.add_points_from_xy(islands, x="Longitude", y="Latitude")

    m.add_basemap("SATELLITE")
    m.to_streamlit(height=500)
