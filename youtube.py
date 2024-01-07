#import packages
from googleapiclient.discovery import build
import pymongo
import psycopg2
import pandas as pd
import streamlit as st

#api key
def api_connect():
    Api_Id="AIzaSyBXi8kcJxE5_hQ73r2kdAG6KD-TN03taA4"
    api_service_name="youtube"
    api_version="v3"
    youtube=build(api_service_name,api_version,developerKey=Api_Id)
    return youtube
youtube=api_connect()

#channel info
def get_channel_info(channel_id):
    request=youtube.channels().list(
                    part="snippet,ContentDetails,statistics",
                    id=channel_id
    )
    response=request.execute()
    for i in response['items']:
        data=dict(Channel_Name=i['snippet']['title'],
                Channel_Id=i['id'],
                Subscribers=i['statistics']['subscriberCount'],
                View=i['statistics']['viewCount'],
                Total_Videos=i['statistics']['videoCount'],
                Channel_Description=i['snippet']['description'],
                Playlist_Id=i['contentDetails']['relatedPlaylists']['uploads'])
    return data
    
#channel videos
def get_channel_videos(channel_id):
    video_ids = []
    # get Uploads playlist id
    res = youtube.channels().list(id=channel_id, 
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    
    while True:
        res = youtube.playlistItems().list( 
                                           part = 'snippet',
                                           playlistId = playlist_id, 
                                           maxResults = 50,
                                           pageToken = next_page_token).execute()
        
        for i in range(len(res['items'])):
            video_ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break
    return video_ids
        
#video info
def get_video_info(video_ids):

    video_data = []

    for video_id in video_ids:
        request = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id= video_id)
        response = request.execute()

        for item in response["items"]:
            data = dict(Channel_Name = item['snippet']['channelTitle'],
                        Channel_Id = item['snippet']['channelId'],
                        Video_Id = item['id'],
                        Title = item['snippet']['title'],
                        Tags = item['snippet'].get('tags'),
                        Thumbnail = item['snippet']['thumbnails']['default']['url'],
                        Description = item['snippet']['description'],
                        Published_Date = item['snippet']['publishedAt'],
                        Duration = item['contentDetails']['duration'],
                        Views = item['statistics']['viewCount'],
                        Likes = item['statistics'].get('likeCount'),
                        Comments = item['statistics'].get('commentCount'),
                        Favorite_Count = item['statistics']['favoriteCount'],
                        Definition = item['contentDetails']['definition'],
                        Caption_Status = item['contentDetails']['caption']
                        )
            video_data.append(data)
    return video_data

#comment info
def get_comment_info(video_ids):
        Comment_Information = []
        try:
                for video_id in video_ids:

                        request = youtube.commentThreads().list(
                                part = "snippet",
                                videoId = video_id,
                                maxResults = 50
                                )
                        response5 = request.execute()
                        
                        for item in response5["items"]:
                                comment_information = dict(
                                        Comment_Id = item["snippet"]["topLevelComment"]["id"],
                                        Video_Id = item["snippet"]["videoId"],
                                        Comment_Text = item["snippet"]["topLevelComment"]["snippet"]["textOriginal"],
                                        Comment_Author = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                                        Comment_Published = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"])

                                Comment_Information.append(comment_information)
        except:
                pass
                
        return Comment_Information

#playlist info
def get_playlist_info(channel_id):
    All_data = []
    next_page_token = None
    next_page = True
    while next_page:

        request = youtube.playlists().list(
            part="snippet,contentDetails",
            channelId=channel_id,
            maxResults=50,
            pageToken=next_page_token
            )
        response = request.execute()

        for item in response['items']: 
            data={'Playlist_Id':item['id'],
                    'Title':item['snippet']['title'],
                    'Channel_Id':item['snippet']['channelId'],
                    'Channel_Name':item['snippet']['channelTitle'],
                    'PublishedAt':item['snippet']['publishedAt'],
                    'Video_Count':item['contentDetails']['itemCount']}
            All_data.append(data)
        next_page_token = response.get('nextPageToken')
        if next_page_token is None:
            next_page=False
    return All_data

#mongodb connect
client=pymongo.MongoClient("mongodb+srv://nsv5901:nitish5901@cluster0.6h8xh1s.mongodb.net/?retryWrites=true&w=majority")
db=client['Youtube_data']

#channel details
def channel_details(channel_id):
    ch_details = get_channel_info(channel_id)
    pl_details = get_playlist_info(channel_id)
    video_ids = get_channel_videos(channel_id)
    vi_details = get_video_info(video_ids)
    com_details = get_comment_info(video_ids)

    coll1 = db["channel_details"]
    coll1.insert_one({"channel_information":ch_details,"playlist_information":pl_details,"video_information":vi_details,
                     "comment_information":com_details})
    
    return "upload completed successfully"

#creating channels table in pgsql 
def channels_table():
        mydb = psycopg2.connect(host="localhost",
                user="postgres",
                password="nitish5901",
                database= "youtube_data",
                port = "5432"
                )
        cursor = mydb.cursor()

        drop_query='''drop table if exists channels'''
        cursor.execute(drop_query)
        mydb.commit()

        try:
                create_query = '''create table if not exists channels(Channel_Name varchar(100),
                                Channel_Id varchar(80) primary key, 
                                Subscribers bigint, 
                                View bigint,
                                Total_Videos int,
                                Channel_Description text,
                                Playlist_Id varchar(50))'''
                cursor.execute(create_query)
                mydb.commit()
        except:
                print("channels table already created")

        ch_list = []
        db = client["Youtube_data"]
        coll1 = db["channel_details"]
        for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
                ch_list.append(ch_data["channel_information"])
        df = pd.DataFrame(ch_list)

        for index,row in df.iterrows():
                insert_query='''insert into channels(Channel_Name,
                                                        Channel_Id,
                                                        Subscribers,
                                                        View,
                                                        Total_Videos,
                                                        Channel_Description,
                                                        Playlist_Id)
                                                        
                                                        values(%s,%s,%s,%s,%s,%s,%s)'''
                values=(row['Channel_Name'],
                        row["Channel_Id"],
                        row['Subscribers'],
                        row['View'],
                        row['Total_Videos'],
                        row['Channel_Description'],
                        row['Playlist_Id'])
                try:
                        cursor.execute(insert_query,values)
                        mydb.commit()
                except:
                        print("exists")


#creating playlist table 
def playlist_table():
        mydb = psycopg2.connect(host="localhost",
                user="postgres",
                password="nitish5901",
                database= "youtube_data",
                port = "5432"
                )
        cursor = mydb.cursor()

        drop_query='''drop table if exists playlists'''
        cursor.execute(drop_query)
        mydb.commit()

        try:
                create_query = '''create table if not exists playlists(Playlist_Id varchar(100) primary key,
                                                                        Title varchar(100), 
                                                                        Channel_Id varchar(80),
                                                                        Channel_Name varchar(100),
                                                                        PublishedAt timestamp,
                                                                        Video_Count int)'''
                cursor.execute(create_query)
                mydb.commit()
        except:
                print("channels table already created")

        pl_list = []
        db = client["Youtube_data"]
        coll1 = db["channel_details"]
        for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
                for i in range(len(pl_data['playlist_information'])):
                        pl_list.append(pl_data["playlist_information"][i])
        df = pd.DataFrame(pl_list)

        
        cursor = mydb.cursor()
        for index,row in df.iterrows():
                insert_query='''insert into playlists(Playlist_Id,
                                                        Title,
                                                        Channel_Id,
                                                        Channel_Name,
                                                        PublishedAt,
                                                        Video_Count
                                                        )
                                                        
                                                        values(%s,%s,%s,%s,%s,%s)'''
                values=(row['Playlist_Id'],
                        row['Title'],
                        row['Channel_Id'],
                        row['Channel_Name'],
                        row['PublishedAt'],
                        row['Video_Count'])
                
                cursor.execute(insert_query,values)
                mydb.commit()






#creating video table pgsql
def video_table():
      
        mydb = psycopg2.connect(host="localhost",
                user="postgres",
                password="nitish5901",
                database= "youtube_data",
                port = "5432"
                )
        cursor = mydb.cursor()

        drop_query='''drop table if exists videos'''
        cursor.execute(drop_query)
        mydb.commit()

        try:
                create_query = '''create table if not exists videos(Channel_Name varchar(100),
                                                                Channel_Id varchar(100),
                                                                Video_Id varchar(30),
                                                                Title varchar(150),
                                                                Tags text,
                                                                Thumbnail varchar(200),
                                                                Description text,
                                                                Published_Date timestamp,
                                                                Duration interval,
                                                                Views bigint,
                                                                Likes bigint,
                                                                Comments int,
                                                                Favorite_Count int,
                                                                Definition varchar(10),
                                                                Caption_Status varchar(50)
                                                                )'''
                cursor.execute(create_query)
                mydb.commit()
        except:
                print("channels table already created")

        vl_list = []
        db = client["Youtube_data"]
        coll1 = db["channel_details"]
        for vl_data in coll1.find({},{"_id":0,"video_information":1}):
                for i in range(len(vl_data["video_information"])):
                        vl_list.append(vl_data["video_information"][i])
        df2 = pd.DataFrame(vl_list)

        for index, row in df2.iterrows():
                insert_query = '''
                        INSERT INTO videos (Channel_Name,
                                Channel_Id,
                                Video_Id, 
                                Title, 
                                Tags,
                                Thumbnail,
                                Description, 
                                Published_Date,
                                Duration, 
                                Views, 
                                Likes,
                                Comments,
                                Favorite_Count, 
                                Definition, 
                                Caption_Status 
                                )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

                        '''
                values = (
                        row['Channel_Name'],
                        row['Channel_Id'],
                        row['Video_Id'],
                        row['Title'],
                        row['Tags'],
                        row['Thumbnail'],
                        row['Description'],
                        row['Published_Date'],
                        row['Duration'],
                        row['Views'],
                        row['Likes'],
                        row['Comments'],
                        row['Favorite_Count'],
                        row['Definition'],
                        row['Caption_Status'])
                                        
                try:    
                        cursor.execute(insert_query,values)
                        mydb.commit()
                except:
                        print("videos values already inserted in the table")

#creating comment table in pgsql
def comments_table():
    
    mydb = psycopg2.connect(host="localhost",
                user="postgres",
                password="nitish5901",
                database= "youtube_data",
                port = "5432"
                )
    cursor = mydb.cursor()

    drop_query = "drop table if exists comments"
    cursor.execute(drop_query)
    mydb.commit()

    try:
        create_query = '''CREATE TABLE if not exists comments(Comment_Id varchar(100) primary key,
                       Video_Id varchar(80),
                       Comment_Text text, 
                       Comment_Author varchar(150),
                       Comment_Published timestamp)'''
        cursor.execute(create_query)
        mydb.commit()
        
    except:
        print("Commentsp Table already created")

    com_list = []
    db = client["Youtube_data"]
    coll1 = db["channel_details"]
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    df3 = pd.DataFrame(com_list)


    for index, row in df3.iterrows():
            insert_query = '''
                INSERT INTO comments (Comment_Id,
                                      Video_Id ,
                                      Comment_Text,
                                      Comment_Author,
                                      Comment_Published)
                VALUES (%s, %s, %s, %s, %s)

            '''
            values = (
                row['Comment_Id'],
                row['Video_Id'],
                row['Comment_Text'],
                row['Comment_Author'],
                row['Comment_Published']
            )
            try:
                cursor.execute(insert_query,values)
                mydb.commit()
            except:
               print("This comments are already exist in comments table")

#table function
def tables():
    channels_table()
    playlist_table()
    video_table()
    comments_table()
    return "Tables Created successfully"

#streamlit
def show_channels_table():
        ch_list = []
        db = client["Youtube_data"]
        coll1 = db["channel_details"]
        for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
                ch_list.append(ch_data["channel_information"])
        df = st.dataframe(ch_list)
        return df

def show_playlist_table():
        pl_list = []
        db = client["Youtube_data"]
        coll1 = db["channel_details"]
        for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
                for i in range(len(pl_data['playlist_information'])):
                        pl_list.append(pl_data["playlist_information"][i])
        df = st.dataframe(pl_list)
        return df

def show_video_table():
            vl_list = []
            db = client["Youtube_data"]
            coll1 = db["channel_details"]
            for vl_data in coll1.find({},{"_id":0,"video_information":1}):
                    for i in range(len(vl_data["video_information"])):
                            vl_list.append(vl_data["video_information"][i])
            df2 = st.dataframe(vl_list)
            return df2

def show_comments_table():
    com_list = []
    db = client["Youtube_data"]
    coll1 = db["channel_details"]
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    df3 = st.dataframe(com_list)
    return df3

with st.sidebar:
    st.title(":red[YOUTUBE DATA HARVESTING AND WAREHOUSING]")
    st.header("SKILL TAKE AWAY")
    st.caption('Python scripting')
    st.caption("Data Collection")
    st.caption("MongoDB")
    st.caption("API Integration")
    st.caption(" Data Managment using MongoDB and SQL")
    
channel_id = st.text_input("Enter the Channel id")
channels = channel_id.split(',')
channels = [ch.strip() for ch in channels if ch]

if st.button("Collect and Store data"):
    for channel in channels:
        ch_ids = []
        db = client["Youtube_data"]
        coll1 = db["channel_details"]
        for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
            ch_ids.append(ch_data["channel_information"]["Channel_Id"])
        if channel in ch_ids:
            st.success("Channel details of the given channel id: " + channel + " already exists")
        else:
            output = channel_details(channel)
            st.success(output)
            
if st.button("Migrate to SQL"):
    display = tables()
    st.success(display)
    
show_table = st.radio("SELECT THE TABLE FOR VIEW",(":green[channels]",":orange[playlists]",":red[videos]",":blue[comments]"))

if show_table == ":green[channels]":
    show_channels_table()
elif show_table == ":orange[playlists]":
    show_playlist_table()
elif show_table ==":red[videos]":
    show_video_table()
elif show_table == ":blue[comments]":
    show_comments_table()

#SQL connection
mydb = psycopg2.connect(host="localhost",
            user="postgres",
            password="nitish5901",
            database= "youtube_data",
            port = "5432"
            )
cursor = mydb.cursor()
    
question = st.selectbox(
    'Please Select Your Question',
    ('1. All the videos and the Channel Name',
     '2. Channels with most number of videos',
     '3. 10 most viewed videos',
     '4. Comments in each video',
     '5. Videos with highest likes',
     '6. likes of all videos',
     '7. views of each channel',
     '8. videos published in the year 2022',
     '9. average duration of all videos in each channel',
     '10. videos with highest number of comments'))

if question == '1. All the videos and the Channel Name':
    query1 = "select Title as videos, Channel_Name as ChannelName from videos;"
    cursor.execute(query1)
    mydb.commit()
    t1=cursor.fetchall()
    st.write(pd.DataFrame(t1, columns=["Video Title","Channel Name"]))

elif question == '2. Channels with most number of videos':
    query2 = "select Channel_Name as ChannelName,Total_Videos as NO_Videos from channels order by Total_Videos desc;"
    cursor.execute(query2)
    mydb.commit()
    t2=cursor.fetchall()
    st.write(pd.DataFrame(t2, columns=["Channel Name","No Of Videos"]))

elif question == '3. 10 most viewed videos':
    query3 = '''select Views as views , Channel_Name as ChannelName,Title as VideoTitle from videos 
                        where Views is not null order by Views desc limit 10;'''
    cursor.execute(query3)
    mydb.commit()
    t3 = cursor.fetchall()
    st.write(pd.DataFrame(t3, columns = ["views","channel Name","video title"]))

elif question == '4. Comments in each video':
    query4 = "select Comments as No_comments ,Title as VideoTitle from videos where Comments is not null;"
    cursor.execute(query4)
    mydb.commit()
    t4=cursor.fetchall()
    st.write(pd.DataFrame(t4, columns=["No Of Comments", "Video Title"]))

elif question == '5. Videos with highest likes':
    query5 = '''select Title as VideoTitle, Channel_Name as ChannelName, Likes as LikesCount from videos 
                       where Likes is not null order by Likes desc;'''
    cursor.execute(query5)
    mydb.commit()
    t5 = cursor.fetchall()
    st.write(pd.DataFrame(t5, columns=["video Title","channel Name","like count"]))

elif question == '6. likes of all videos':
    query6 = '''select Likes as likeCount,Title as VideoTitle from videos;'''
    cursor.execute(query6)
    mydb.commit()
    t6 = cursor.fetchall()
    st.write(pd.DataFrame(t6, columns=["like count","video title"]))

elif question == '7. views of each channel':
    query7 = "select Channel_Name as ChannelName, View as Channelviews from channels;"
    cursor.execute(query7)
    mydb.commit()
    t7=cursor.fetchall()
    st.write(pd.DataFrame(t7, columns=["channel name","total views"]))

elif question == '8. videos published in the year 2022':
    query8 = '''select Title as Video_Title, Published_Date as VideoRelease, Channel_Name as ChannelName from videos 
                where extract(year from Published_Date) = 2022;'''
    cursor.execute(query8)
    mydb.commit()
    t8=cursor.fetchall()
    st.write(pd.DataFrame(t8,columns=["Name", "Video Publised On", "ChannelName"]))

elif question == '9. average duration of all videos in each channel':
    query9 =  "SELECT Channel_Name as ChannelName, AVG(Duration) AS average_duration FROM videos GROUP BY Channel_Name;"
    cursor.execute(query9)
    mydb.commit()
    t9=cursor.fetchall()
    t9 = pd.DataFrame(t9, columns=['ChannelTitle', 'Average Duration'])
    T9=[]
    for index, row in t9.iterrows():
        channel_title = row['ChannelTitle']
        average_duration = row['Average Duration']
        average_duration_str = str(average_duration)
        T9.append({"Channel Title": channel_title ,  "Average Duration": average_duration_str})
    st.write(pd.DataFrame(T9))

elif question == '10. videos with highest number of comments':
    query10 = '''select Title as VideoTitle, Channel_Name as ChannelName, Comments as Comments from videos 
                       where Comments is not null order by Comments desc;'''
    cursor.execute(query10)
    mydb.commit()
    t10=cursor.fetchall()
    st.write(pd.DataFrame(t10, columns=['Video Title', 'Channel Name', 'NO Of Comments']))