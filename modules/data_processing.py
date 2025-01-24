import pandas as pd
import numpy as np 

def drop_columns(data: pd.DataFrame)->pd.DataFrame:
    # drop columns 
    to_drop: list = ['resource_state','type','start_date','utc_offset','kudos_count', 'comment_count','athlete_count','photo_count',\
           'trainer', 'commute', 'manual','heartrate_opt_out', 'display_hide_heartrate_option','upload_id_str', 'external_id',
       'from_accepted_tag', 'total_photo_count', 'has_kudoed','athlete.id', 'athlete.resource_state','timezone','average_cadence','location_city', 'location_state', 'location_country']
    data.drop(to_drop,axis=1,inplace=True)
    return data 

def fix_date_time(data:pd.DataFrame)-> pd.DataFrame:
    # fix date_time 
    data.start_date_local = pd.to_datetime(data.start_date_local)
    data['date']=   data.start_date_local.dt.date
    data['year'] =  data.start_date_local.dt.year
    data['month'] = data.start_date_local.dt.month
    data['day'] =   data.start_date_local.dt.day
    data['start_time'] = data.start_date_local.dt.time
    data.drop('start_date_local',axis=1,inplace=True)
    return data 
def only_runs(data:pd.DataFrame)->pd.DataFrame:
    runs_type = ['Run', 'Hike', 'TrailRun']
    data = data.query("sport_type in @runs_type")
    data['distance_km'] = np.round(data.distance/1000,2)
    data['moving_time_h'] = pd.to_datetime(data['moving_time'],unit='s')
    return data

def make_zones(data:pd.DataFrame)->pd.DataFrame:
    zones = [0,135,148,162,175,210]
    zones_label= ['zone 1', 'zone 2', 'zone 3', 'zone 4','zone 5']
    data['avg_zones']=pd.cut(data['average_heartrate'],bins= zones,labels = zones_label)
    data['max_zones']=pd.cut(data['max_heartrate'],bins= zones,labels = zones_label)
    return data 
def ms_to_kmh(data:pd.DataFrame)->pd.DataFrame:
    data['avg_pace'] = 60/(data['average_speed']*3.6)
    return data


def preprocess(data:pd.DataFrame)->pd.DataFrame:
    data = drop_columns(data)
    data = fix_date_time(data)
    data = only_runs(data)
    data = make_zones(data)
    data = ms_to_kmh(data)
    return data 


