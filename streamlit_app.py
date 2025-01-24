import streamlit as st
from modules.utils import get_auth_url, get_access_token,get_activities,get_secrets
from modules.data_processing import preprocess
import pandas as pd
import plotly.express as px
import plotly 
import plotly.graph_objects as go
import numpy as np 
import folium
from streamlit_folium import st_folium,folium_static
import polyline


STRAVA_CLIENT_ID,STRAVA_CLIENT_SECRET, REDIRECT_URI = get_secrets()







st.title("🎈 Strava Improved")
st.write(
    "Let's have a deep dive into your strava history and get some new insights!"
)
login_method = st.selectbox('how do you want to provide your data?',("Strava","File"))
if login_method =="Strava":
    if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET:
        raise Exception("Secrets not found! Ensure your environment variables are set.")


    auth_url = get_auth_url(STRAVA_CLIENT_ID, REDIRECT_URI)
    st.write(f'click on the following link to allow the app to access your strava data: {auth_url}')
    st.write("After authorization, Strava will redirect to a blank page with a 'code' parameter Paste the 'code' from the redirect URL below" )
    auth_code = st.text_input('authorization code').strip()
    token_response = None

if st.button('Retrieve data'):
    if login_method =="Strava":
        token_response = get_access_token(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, auth_code)
        print(token_response)
        access_token = token_response.get("access_token")
        activities = get_activities(access_token)
        activities = pd.json_normalize(activities)
        print(auth_code)
    else: 
        activities = pd.read_pickle('data/actvities.csv')
    activities_clean = preprocess(activities)
    tab1, tab2, tab3 = st.tabs(["Overview", "In Depth", "Maps"])
    with tab1:
        with st.container():
            st.header("Summary of your performances")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"total distance ran:{sum(activities_clean['distance_km'])}")
                st.write(f'Total number of runs:{activities_clean["distance_km"].shape[0]}')
            with col2:
                st.write(f"average running speed:{activities_clean['avg_pace'].mean()}\'/km")
                #st.write(f"total run time:{sum(activities_clean['moving_time_h'])}")
                st.write(activities_clean.head())
        
        fig_dist = px.line(activities_clean, x="date", y="distance_km",color='sport_type',text="distance_km", title='Activity distance(km) over time')
        st.plotly_chart(fig_dist)
        layout = plotly.graph_objs.Layout(yaxis={
        'type': 'date',
        'tickformat': '%H:%M:%S'
        }
        )
        fig_duration = px.scatter(activities_clean, x="date", y="moving_time_h",color='sport_type', title='Activities duration over time')
        figure = go.Figure(data=fig_duration)
        figure.update_layout(yaxis_tickformat="%H:%M:%S")
        st.plotly_chart(figure)
    
    with tab2:
        avg_zones = activities_clean.query("@activities_clean['avg_zones'].notna()")
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                fig_zone_avg = px.pie(avg_zones, values='average_heartrate', names='avg_zones', title= "Proportion of average zone",hover_data=['average_heartrate'])
                fig_zone_avg.update(layout_showlegend=False)
                fig_zone_avg.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_zone_avg)
            with col2:
                fig_zone_max = px.pie(avg_zones, values='max_heartrate', names='max_zones', title= "Proportion of maximum zone",hover_data = ['max_heartrate'])
                fig_zone_max.update(layout_showlegend=False)
                fig_zone_max.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_zone_max)

            year_month_zones =activities_clean.groupby(['year','month','avg_zones'],observed=True)
            year_month =activities_clean.groupby(['year','month'],observed=True)
            a = year_month_zones.average_heartrate.count()
            b = year_month.average_heartrate.count()
            propzone= a/b
            propzones_df = propzone.reset_index()
            propzones_df['day']=1
            propzones_df['date'] = pd.to_datetime(propzones_df[['year', 'month','day']])
            propzones_df.drop(['year','month','day'],axis=1,inplace=True)
            fig_zone_prop = px.bar(propzones_df, x="date", y="average_heartrate", color="avg_zones", text_auto='.2%', title="Proportion of time spent in zone", category_orders={"avg_zones": ['zone 1', 'zone 2', 'zone 3', 'zone 4']},
                        labels={"average_heartrate": "Proportion in zone", "avg_zones": "Zone", "date": "Period"})
            st.plotly_chart(fig_zone_prop)
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                run_only = ['Run', 'TrailRun']
                run_only_df = activities_clean.query("sport_type in @run_only")
                fig_pace_dist = px.histogram(run_only_df,x='avg_pace', color= 'sport_type',
                            marginal="violin",opacity=0.9)
                st.plotly_chart(fig_pace_dist)
            with col2:
                fig_pace_time = px.line(run_only_df,x= 'date',y='avg_pace',color = 'sport_type')
                st.plotly_chart(fig_pace_time)
            distance_choice =st.selectbox("Maximum distance to consider",("5KM", "10KM", "Half-marathon","Marathon","Ultra"))
            distances = {"5KM":5, "10KM":10, "Half-marathon":21,"Marathon":42,"Ultra":500}
            pace_distance = run_only_df.loc[np.round(run_only_df['distance_km'],0)<=distances[distance_choice]]
            fig_pace_distance = px.scatter(pace_distance,x= 'date',y='avg_pace',color = 'sport_type')
            st.plotly_chart(fig_pace_distance)
        
    with tab3:
        maps_df = activities[['id','map.id','map.summary_polyline', 'map.resource_state']]
        maps_poly_non_null = maps_df[maps_df['map.summary_polyline'] != '']
        # folium support for streamlit through streamlit-folium
        s = folium.Map(location=[48.2081, 16.3713],tiles='OpenTopoMap', zoom_start= 10)
        maps_poly_non_null['decoded'] = maps_poly_non_null['map.summary_polyline'].apply(polyline.decode)
        maps_and_co = pd.merge(maps_poly_non_null,activities_clean,how='inner',on='id')
        for i in maps_and_co.index: 
            dist = maps_and_co['distance_km'].iloc[i]
            dd = maps_and_co['date'].iloc[i]
            text = f"Ran {dist} km on {dd}."
            start = maps_and_co['start_latlng'].iloc[i]
            end = maps_and_co['end_latlng'].iloc[i]
            folium.PolyLine(locations=maps_and_co['decoded'].loc[i],tooltip=text).add_to(s)
            folium.Marker(
            location=start,
            tooltip="Start point",
            icon=folium.Icon(icon= 'play',color="green")).add_to(s)
            folium.Marker(
                location=end,
                tooltip="End Point",
                icon=folium.Icon(icon='flag',color="red")).add_to(s)
        if tab3:   
            st_map_folium = folium_static(s,width=725)
        




        


