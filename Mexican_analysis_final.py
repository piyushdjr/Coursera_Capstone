#!/usr/bin/env python
# coding: utf-8

# # Let us Start by Importing Libraries required

# In[1]:


import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import requests
from bs4 import BeautifulSoup
import geocoder
import os
import folium # map rendering library
from geopy.geocoders import Nominatim # convert an address into latitude and longit # Matplotlib and associated plotting modules
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
get_ipython().run_line_magic('matplotlib', 'inline')

print("done")


# ### Now we define a function to get the geocodes i.e latitude and longitude of a given location using geopy.
# 

# In[2]:


def geo_location(address):
   # get geo location of address
    geolocator = Nominatim(user_agent="ny_explorer") 
    location = geolocator.geocode(address)
    latitude = location.latitude
    longitude = location.longitude
    return latitude,longitude


# ### We define a function to intract with FourSquare API and get top 100 venues within a radius of 1000 metres for a given latitude and longitude. Below function will return us the venue id , venue name and category.

# In[3]:


def get_venues(lat,lng):
    
    #set variables
    radius=1000
    LIMIT=100
    CLIENT_ID = 'MZ2QVF3VPSM5WLV1GOB44VQPSQDZVUQ4BRBITS02NT2W0Z0W' # your Foursquare ID
    CLIENT_SECRET ='USP4F2JXEXB2LMU1MMGGXUIJOYJTVM3QL30YVYXJPK5ATAD1' # your Foursquare Secret
    VERSION = '20180605' # Foursquare API version
    
    #url to fetch data from foursquare api
    url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
    
    # get all the data
    results = requests.get(url).json()
    venue_data= results['response']['groups'][0]['items']
    venue_details=[]
    for row in venue_data:
        try:
            venue_id=row['venue']['id']
            venue_name=row['venue']['name']
            venue_category=row['venue']['categories'][0]['name']
            venue_details.append([venue_id,venue_name,venue_category])
        except KeyError:
            pass
        
    column_names=['ID','Name','Category']
    df = pd.DataFrame(venue_details,columns=column_names)
    return df


# ### Now we will define a function to get venue details like like count , rating , tip counts for a given venue id. This will be used for ranking.

# In[4]:


CLIENT_IDI = 'Z4A4QJX4ILQY5K0PCCEBGQSC2K4LZJGFH3N24WFTZ4V5GMFR' # your Foursquare ID
CLIENT_SECRETI ='E5XKEDSOCMSRFLDTWDSHRRXIFIKC3WETYCLFKBT0GFBUYGGV'# your Foursquare Secret
VERSION = '20180605' # Foursquare API version


# In[5]:



def get_venue_details(venue_id):
        
    
    
    #url to fetch data from foursquare api
    url = 'https://api.foursquare.com/v2/venues/{}?&client_id={}&client_secret={}&v={}'.format(
            venue_id,
            CLIENT_IDI, 
            CLIENT_SECRETI, 
            VERSION)
    
    # get all the data
    results = requests.get(url).json()
    venue_data=results['response']['venue']
    venue_details=[]
    try:
        venue_id=venue_data['id']
        venue_name=venue_data['name']
        venue_likes=venue_data['likes']['count']
        venue_rating=venue_data['rating']
        venue_tips=venue_data['tips']['count']
        venue_details.append([venue_id,venue_name,venue_likes,venue_rating,venue_tips])
    except KeyError:
        pass
        
    column_names=['ID','Name','Likes','Rating','Tips']
    df = pd.DataFrame(venue_details,columns=column_names)
    return df


# In[ ]:





# ### Now we define a funtion to get the new york city data such as Boroughs, Neighborhoods along with their latitude and longitude

# In[6]:


def get_new_york_data():
    url='https://cocl.us/new_york_dataset'
    resp=requests.get(url).json()
    # all data is present in features label
    features=resp['features']
    
    # define the dataframe columns
    column_names = ['Borough', 'Neighborhood', 'Latitude', 'Longitude'] 
    # instantiate the dataframe
    new_york_data = pd.DataFrame(columns=column_names)
    
    for data in features:
        borough = data['properties']['borough'] 
        neighborhood_name = data['properties']['name']
        
        neighborhood_latlon = data['geometry']['coordinates']
        neighborhood_lat = neighborhood_latlon[1]
        neighborhood_lon = neighborhood_latlon[0]
    
        new_york_data = new_york_data.append({'Borough': borough,
                                          'Neighborhood': neighborhood_name,
                                          'Latitude': neighborhood_lat,
                                          'Longitude': neighborhood_lon}, ignore_index=True)
    
    return new_york_data


# In[7]:


# get new york data
new_york_data=get_new_york_data()


# In[8]:


new_york_data.head()


# In[9]:


new_york_data.shape


# In[10]:


#So there are total of 306 different Neighborhoods Venues in New York and 5 Boroughs 


# In[12]:


# title
plt.title('Number of Neighborhood for each Borough in New York City')
#On x-axis
plt.xlabel('Borough', fontsize = 15)
#On y-axis
plt.ylabel('No.of Neighborhood', fontsize=15)
#giving a bar plot
new_york_data.groupby('Borough')['Neighborhood'].count().plot(kind='bar')
#legend
plt.legend()
#displays the plot
plt.show()


# #### Now we will collect Mexican resturants for each Neighborhood

# In[13]:


# prepare neighborhood list that contains mexican resturants
column_names=['Borough', 'Neighborhood', 'ID','Name']
max_rest_ny=pd.DataFrame(columns=column_names)
count=1
for row in new_york_data.values.tolist():
    Borough, Neighborhood, Latitude, Longitude=row
    venues = get_venues(Latitude,Longitude)
    max_resturants=venues[venues['Category']=='Mexican Restaurant']   
    print('(',count,'/',len(new_york_data),')','Mexican Resturants in '+Neighborhood+', '+Borough+':'+str(len(max_resturants)))
    for resturant_detail in max_resturants.values.tolist():
        id, name , category=resturant_detail
        max_rest_ny = max_rest_ny.append({'Borough': Borough,
                                                'Neighborhood': Neighborhood, 
                                                'ID': id,
                                                'Name' : name
                                               }, ignore_index=True)
    count+=1


# In[21]:


max_rest_ny.head()


# In[18]:


max_rest_ny.shape


# ### We have here total 326 Mexican Restaurants 

# In[22]:


plt.figure(figsize=(9,5), dpi = 100)
# title
plt.title('Number of Mexican Resturants for each Borough in New York City')
#On x-axis
plt.xlabel('Borough', fontsize = 15)
#On y-axis
plt.ylabel('No.of Mexican Resturants', fontsize=15)
#giving a bar plot
max_rest_ny.groupby('Borough')['ID'].count().plot(kind='bar')
#legend
plt.legend()
#displays the plot
plt.show()


# ### Brooklyn has largest number of restaurants 

# In[23]:


plt.figure(figsize=(9,5), dpi = 100)
# title
plt.title('Number of Mexican Resturants for each Neighborhood in New York City')
#On x-axis
plt.xlabel('Neighborhood', fontsize = 15)
#On y-axis
plt.ylabel('No.of Mexican Resturants', fontsize=15)
#giving a bar plot
max_rest_ny.groupby('Neighborhood')['ID'].count().nlargest(5).plot(kind='bar')
#legend
plt.legend()
#displays the plot
plt.show()


# In[25]:


max_rest_ny[max_rest_ny['Neighborhood']=='Melrose']


# In[26]:


# prepare neighborhood list that contains Mexican resturants
column_names=['Borough', 'Neighborhood', 'ID','Name','Likes','Rating','Tips']
max_rest_stats_ny=pd.DataFrame(columns=column_names)
count=1


for row in max_rest_ny.values.tolist():
    Borough,Neighborhood,ID,Name=row
    try:
        venue_details=get_venue_details(ID)
        print(venue_details)
        id,name,likes,rating,tips=venue_details.values.tolist()[0]
    except IndexError:
        print('No data available for id=',ID)
        # we will assign 0 value for these resturants as they may have been 
        #recently opened or details does not exist in FourSquare Database
        id,name,likes,rating,tips=[0]*5
    print('(',count,'/',len(max_rest_ny),')','processed')
    max_rest_stats_ny = max_rest_stats_ny.append({'Borough': Borough,
                                                'Neighborhood': Neighborhood, 
                                                'ID': id,
                                                'Name' : name,
                                                'Likes' : likes,
                                                'Rating' : rating,
                                                'Tips' : tips
                                               }, ignore_index=True)
    count+=1
  


# In[27]:



max_rest_stats_ny.head()


# In[28]:



max_rest_stats_ny.shape


# In[29]:



max_rest_ny.shape


# ##### So we got data for all resturants Now lets save this data to a csv sheet. In case we by mistake modify it. As the number of calls to get details for venue are premium call and have limit of 500 per day, we will refer to saved data sheet csv if required

# In[30]:


max_rest_stats_ny.to_csv('mexican_rest_stats_ny.csv', index=False)


# In[31]:


mexican_rest_stats_ny_csv=pd.read_csv('mexican_rest_stats_ny.csv')


# In[32]:


mexican_rest_stats_ny_csv.shape


# In[33]:


mexican_rest_stats_ny_csv.head()


# In[34]:


mexican_rest_stats_ny_csv.info()


# In[35]:


max_rest_stats_ny['Likes']=max_rest_stats_ny['Likes'].astype('float64')


# In[36]:


max_rest_stats_ny['Tips']=max_rest_stats_ny['Tips'].astype('float64')


# In[37]:


max_rest_stats_ny.info()


# In[38]:



# Resturant with maximum Likes
max_rest_stats_ny.iloc[max_rest_stats_ny['Likes'].idxmax()]


# In[39]:


# Resturant with maximum Rating
max_rest_stats_ny.iloc[max_rest_stats_ny['Rating'].idxmax()]


# In[40]:


# Resturant with maximum Tips
max_rest_stats_ny.iloc[max_rest_stats_ny['Tips'].idxmax()]


# ###### Now lets visualize neighborhood with maximum average rating of resturants

# In[41]:


ny_neighborhood_stats=max_rest_stats_ny.groupby('Neighborhood',as_index=False).mean()[['Neighborhood','Rating']]
ny_neighborhood_stats.columns=['Neighborhood','Average Rating']


# In[42]:


ny_neighborhood_stats.sort_values(['Average Rating'],ascending=False).head(10)


# #### Above are the top neighborhoods with top average rating of Mexican resturants

# In[43]:


ny_borough_stats=max_rest_stats_ny.groupby('Borough',as_index=False).mean()[['Borough','Rating']]
ny_borough_stats.columns=['Borough','Average Rating']


# In[44]:


ny_borough_stats.sort_values(['Average Rating'],ascending=False).head()


# #### Similarly these are the average rating of Mexican Resturants for each Borough

# In[45]:


plt.figure(figsize=(9,5), dpi = 100)
# title
plt.title('Average rating of Mexican Resturants for each Borough')
#On x-axis
plt.xlabel('Borough', fontsize = 15)
#On y-axis
plt.ylabel('Average Rating', fontsize=15)
#giving a bar plot
max_rest_stats_ny.groupby('Borough').mean()['Rating'].plot(kind='bar')
#legend
plt.legend()
#displays the plot
plt.show()


# ### We will consider all the neighborhoods with average rating greater or equal 9.0 to visualize on map

# In[54]:


ny_neighborhood_stats=ny_neighborhood_stats[ny_neighborhood_stats['Average Rating']>=9.0]          


# In[55]:


ny_neighborhood_stats


# In[56]:


ny_neighborhood_stats=pd.merge(ny_neighborhood_stats,new_york_data, on='Neighborhood')


# In[57]:


ny_neighborhood_stats=ny_neighborhood_stats[['Borough','Neighborhood','Latitude','Longitude','Average Rating']]


# In[59]:


ny_neighborhood_stats


# In[60]:


# create map and display it
ny_map = folium.Map(location=geo_location('New York'), zoom_start=12)


# In[61]:



# instantiate a feature group for the incidents in the dataframe
incidents = folium.map.FeatureGroup()

# loop through the 100 crimes and add each to the incidents feature group
for lat, lng, in ny_neighborhood_stats[['Latitude','Longitude']].values:
    incidents.add_child(
        folium.CircleMarker(
            [lat, lng],
            radius=10, # define how big you want the circle markers to be
            color='yellow',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6
        )
    )


# In[62]:


#let's add new field to dataframe for labelling 


# In[63]:


ny_neighborhood_stats['Label']=ny_neighborhood_stats['Neighborhood']+', '+ny_neighborhood_stats['Borough']+'('+ny_neighborhood_stats['Average Rating'].map(str)+')'


# In[64]:


ny_neighborhood_stats['Label']=ny_neighborhood_stats['Neighborhood']+', '+ny_neighborhood_stats['Borough']+'('+ny_neighborhood_stats['Average Rating'].map(str)+')'


# In[65]:


ny_map = folium.Map(location=geo_location('New York'), zoom_start=12)

json_url=r'USA New York City neighborhood 20190128.geojson'
ny_map.choropleth(
    geo_data=json_url,
    data=ny_borough_stats,
    columns=['Borough', 'Average Rating'],
    key_on='feature.properties.boro_name',
    fill_color='YlOrRd', 
    fill_opacity=0.7, 
    line_opacity=0.2,
    legend_name='Average Rating'
)
ny_map



# # Conclusion 
# #### We can conclude that Manhattan have the potential market for Mexican restaurants
# #### Astoria(Queens), Blissville(Queens) and Civic Center(Manhattan) have some of the major Mexican Restaurants  
# 

# # Limitations
# #### Based on Foursquare limited Data
# #### Based purely on ratings

# In[ ]:




