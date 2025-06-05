import pandas as pd
import streamlit as st
import plotly.express as px
import re
import base64
## Reading files
st.markdown(
    """
    <style>
    body {
        background-color: black;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)
df=pd.read_csv('netflix_titles.csv')
with open("channels4_profile.jpg", "rb") as image_file:
    encoded = base64.b64encode(image_file.read()).decode()
## Adding picture
st.markdown(
    f"""<div style="margin-left: 9px;">
            <img src="data:image/png;base64,{encoded}" width="150" />
        </div>""",
    unsafe_allow_html=True
)
#Adding title name 
st.markdown("<h1 style='text-align: center;color: red;'>Netflix Content Anaylsis</h1>",unsafe_allow_html=True)
# Date cleaning
df.date_added=df.date_added.str.strip()
df['date_added']=pd.to_datetime(df['date_added'],format="%B %d, %Y")
df['year_added']=df.date_added.dt.year
# adding Date to side bar
min_date = df['date_added'].min()
max_date = df['date_added'].max()
start_date=st.sidebar.date_input("DateAdded", value=min_date,min_value=min_date,max_value=max_date)
end_Date=st.sidebar.date_input("EndDate", value=max_date,min_value=min_date,max_value=max_date)
# setting different pages
page=st.sidebar.radio('Pages',['HomePage','Movies','Series'])
# Data cleaning and feature engineering

df.release_year=df.release_year.astype(object)
df['director']=df['director'].fillna("Not identified") 
df['cast']=df['cast'].fillna("Not identified") 
df['country'] = df['country'].fillna("Not identified")
df['new'] = df['country'].str.split(',')
df = df.explode('new')
df['new'] = df['new'].str.strip()
df = df.reset_index(drop=True)
df['category'] = df['listed_in'].str.split(',')
df = df.explode('category')
df['category'] = df['category'].str.strip()
df = df.reset_index(drop=True)
series = df[df['duration'].str.contains(r'Season[s]?', case=False, na=False)].copy()
movies=df[df['type']=='Movie'].copy()
keywords = ['season', 'seasons']
pattern = r'(\d+)\s+(season|seasons)'
series[['number_ofseasons','season_type']]= series['duration'].str.extract(pattern, flags=re.IGNORECASE)
pattern=r'(\d+)'
movies['movies_minutes']=movies['duration'].str.extract(pattern,flags=re.IGNORECASE,expand=True)
df.loc[movies.index, 'movies_minutes'] = movies['movies_minutes']
df.loc[series.index, 'number_ofseasons'] = series['number_ofseasons']
list=df['cast'].to_list()
def count_cast(row):
    if row != 'Not identified' and isinstance(row, str):
        members = row.split(',')
        count = 0
        for i in range(len(members)):
            if members[i].strip() != 'Not identified':
                count += 1
        return count
    else:
        return 0
df['count_cast'] = df['cast'].apply(count_cast)

  #series

df['number_ofseasons']=df.number_ofseasons.fillna(0)
df['movies_minutes']=df.movies_minutes.fillna(0)
df_filtered=df[(df.date_added>=str(start_date))&(df.date_added<=str(end_Date))]
distrubuttion=df_filtered.groupby('type')['show_id'].count().reset_index()#could do it with value_counts as well !
distrubuttion.type=distrubuttion.type.str.strip()
# creating Pages 
if page=='HomePage':
    dropped=df.drop_duplicates(subset=['cast'])
    countofcontent = dropped['show_id'].drop_duplicates().count() # calculating measure for cards
    totalnumberofyears= int(max(df['year_added'])-min(df['year_added']))
    totalnumberofcast=dropped.groupby('cast')['count_cast'].sum().reset_index()
    actorscount=totalnumberofcast.count_cast.sum()

# Display dynamic cards
    col1, col2,col3 = st.columns(3)
    col1.metric("Total Number of Shows/movies🎬📺", f"{countofcontent}")
    col2.metric("Total Number of Years⏳", f"{totalnumberofyears}")
    col3.metric("Total Number of Actors🎭", f"{actorscount}")


     # Actor name engine Search

    df['count_cast']=df['cast'].apply(count_cast)
    actor_name = st.text_input("Add your favourite actor name: ",key="actor_inputt")
    filtered_df = df_filtered[df_filtered['cast'].str.contains(actor_name, flags=re.IGNORECASE, na=False)]
    if actor_name:
        if not filtered_df.empty:
             st.subheader(f"Titles with {actor_name}")
             st.dataframe(filtered_df.drop_duplicates(subset=['description']))
        else:
            st.info('Not found')
    # Movie Name engine Search
    movie_name = st.text_input("Add your movie name: ",key="movie_inputt")
    moviefind=movies[movies['title'].str.contains(movie_name, flags=re.IGNORECASE, na=False)]
    if movie_name :
        if not moviefind.empty:
            st.subheader(f"Search result for '{movie_name}'")
            st.dataframe(moviefind.drop_duplicates(subset=['description']))
        else:
                st.info("Not Found")
    # Series Name Search
    show_name = st.text_input("Add your series name: ",key="series_inputt")
    show_find=series[series['title'].str.contains(show_name, flags=re.IGNORECASE, na=False)]
    if show_name:
        if not show_find.empty:
            st.subheader(f"Search result for '{show_name}'")
            st.dataframe(show_find.drop_duplicates(subset=['title']))
        else:
             st.info('not found')
    # showing DF for all DATA
    st.subheader('Whole Data')
    st.dataframe(df_filtered)
    # chart showing  Netflix Distrubuition movies VS shows

    fig_type = px.pie(distrubuttion, names='type', values='show_id', title='Netflix Distribution: Movies vs Shows',color_discrete_map = {'Movie': 'red', 'TV Show': '#000000'},color='type') # solid black
    fig_type.update_layout(title={'text': 'Netflix Distribution: Movies vs Shows', 'x': 0.2,'font': {'size': 20, 'color': 'white','family': 'Arial','weight': 'bold' }})
    fig_type.update_traces(textfont=dict(family='Arial', size=14, color='white'),textinfo='label+percent+value') 
    st.plotly_chart(fig_type)
    # 10 top common genre
    genres=df.groupby('category')['show_id'].count().reset_index().head()
    genres.sort_values(by='show_id',ascending=False,inplace=True)
    fig = px.bar(genres,x='category',y='show_id',title='10 Top  Common  Genre',text_auto=True, color_discrete_sequence=['red'])
    fig.update_layout(yaxis_title='Count of genre')
    fig.update_layout(title={'x': 0.3, 'font': {'size': 20, 'color': 'white', 'family': 'Arial','weight':'bold'}},)
    fig.update_layout(xaxis_title={'text': 'category','font': {'size': 14,'color': 'white','family': 'Arial','weight': 'bold'}})
    fig.update_layout(yaxis_title={'text': 'Count of genre','font': {'size': 14,'color': 'white','family': 'Arial','weight': 'bold'}})
    fig.update_yaxes(tickfont=dict(family='arial',weight='bold',size=14))
    fig.update_xaxes(tickfont=dict(family='arial',weight='bold',size=14))
    st.plotly_chart(fig)
    #top countries producing netflix content

    countries = df.groupby('new')['show_id'].count().reset_index()
    countries.sort_values(by='show_id', ascending=False, inplace=True)
    countries = countries.head(10)
    figc = px.bar(data_frame=countries,x='new',y='show_id',title='What are the top countries producing Netflix content?',text_auto=True, color_discrete_sequence=['red'])
    figc.update_layout(yaxis_title='Count of country')
    figc.update_layout(xaxis_title='Country Name')
    figc.update_layout(title={'x': 0.2, 'font': {'size': 20, 'color': 'white', 'family': 'Arial','weight':'bold'}},)
    figc.update_layout(xaxis_title={'text': 'Country Name','font': {'size': 14,'color': 'white','family': 'Arial','weight': 'bold'}})
    figc.update_layout(yaxis_title={'text': 'Count of country','font': {'size': 14,'color': 'white','family': 'Arial','weight': 'bold'}})
    figc.update_yaxes(tickfont=dict(family='arial',weight='bold',size=14))
    figc.update_xaxes(tickfont=dict(family='arial',weight='bold',size=14))
    st.plotly_chart(figc)

    #how has netflix's content volume change overtime 

    df_filtered['year_added']=df_filtered.date_added.dt.year
    yearadded=df_filtered.groupby('year_added')['show_id'].count().reset_index()
    figy=px.line(data_frame=yearadded,x='year_added',y='show_id',color_discrete_sequence=['red'],title="How has Netflix's content volume changed over time?")
    figy.update_xaxes(tickmode='linear')
    figy.update_layout(yaxis_title='Years_added')
    figy.update_layout(xaxis_title='count of content')
    figy.update_layout(title={'x': 0.2, 'font': {'size': 20, 'color': 'white', 'family': 'Arial','weight':'bold'}},)
    figy.update_layout(xaxis_title={'text': 'Years_added','font': {'size': 14,'color': 'white','family': 'Arial','weight': 'bold'}})
    figy.update_layout(yaxis_title={'text': 'count of','font': {'size': 14,'color': 'white','family': 'Arial','weight': 'bold'}})
    figy.update_yaxes(tickfont=dict(family='arial',weight='bold',size=14))
    figy.update_xaxes(tickfont=dict(family='arial',weight='bold',size=14))

    #are tv shows becming more common than movies?

    typeandyear=df_filtered.groupby(['type','year_added'])['show_id'].count().reset_index()#could do it with value_counts as well !
    type_year=px.line(data_frame=typeandyear,y='show_id',x='year_added',color='type',line_group='type',title='Are TV shows becoming more common than movies?',color_discrete_map={'Movie':'red','TV Show':'white'})
    type_year.update_layout(yaxis=dict(title='Count of shows/movies',title_font=dict(size=20)))
    type_year.update_layout(legend=dict(font=dict( size=16)))
    type_year.update_layout(title={'text':'<b>Are TV shows becoming more common than movies?</b>','x': 0.1,'font':{'size':20}})
    st.plotly_chart(figy)
    st.plotly_chart(type_year)
#creating second page movies 

if page == 'Movies':
    #creating base DF
    base_moviefilter = df_filtered[df_filtered.type == 'Movie'].drop_duplicates(subset=['cast'])
    base_moviefilter['count_cast']=df['cast'].apply(count_cast)           

    numberofmovies = base_moviefilter['show_id'].nunique() # count of unique shows
    totalnumberofcast=base_moviefilter.groupby('cast')['count_cast'].sum().reset_index()
    actorscount=totalnumberofcast.count_cast.sum()
    col1, col2 = st.columns(2) # creating variables for cards
    col1.metric("🎬 Total Number of Movies", numberofmovies) # creating card meteric for total number of movies
    col2.metric("Total Number of Actors🎭", f"{actorscount}")


    # User inputs with keys to avoid conflicts
    actor_name = st.text_input("Add your favourite actor name: ", key="actor_input")
    movie_name = st.text_input("Add your movie name: ", key="movie_input")

    # Apply filters
    moviefilter = base_moviefilter.copy()
    if actor_name:
        moviefilter = moviefilter[moviefilter['cast'].str.contains(actor_name, flags=re.IGNORECASE, na=False)]
    if movie_name:
        moviefilter = moviefilter[moviefilter['title'].str.contains(movie_name, flags=re.IGNORECASE, na=False)]
# Here we do conditinal if based on several conditions to result in changing charts in both conditions not just one
    # Display filtered results
    if actor_name and moviefilter.empty:
        st.info(f"No results for actor: {actor_name}")
    elif actor_name:
        st.subheader(f"Titles with {actor_name}")
        st.dataframe(moviefilter.drop_duplicates(subset=['description']))

    if movie_name and moviefilter.empty:
        st.info(f"No results for movie: {movie_name}")
    elif movie_name:
        st.subheader(f"Search result for '{movie_name}'")
        st.dataframe(moviefilter.drop_duplicates(subset=['description']))

    # Chart 1: Top 10 Genres
    genre_count = moviefilter['category'].value_counts().reset_index().head(10)
    figm = px.bar(genre_count, x='category', y='count', title='<b>Top 10 Movie Genres</b>',
                  color_discrete_sequence=['red']).update_layout(title={'x': 0.5})
    st.plotly_chart(figm)

    # Chart 2: Movie duration distribution
    moviefilter['movies_minutes'] = moviefilter['movies_minutes'].astype('int64')
    figmin = px.histogram(moviefilter, x='movies_minutes', nbins=30,
                          title='Movie Duration Distribution (minutes)',
                          color_discrete_sequence=['red'])
    st.plotly_chart(figmin)

    # Chart 3: Top 10 Directors
    top_directors = moviefilter[moviefilter['director'] != 'Not identified']
    top_directors = top_directors['director'].value_counts().reset_index().head(10)
    figd = px.bar(top_directors, x='director', y='count', title='<b>Top 10 Movie Directors</b>',
                  color_discrete_sequence=['red']).update_layout(title={'x': 0.2})
    st.plotly_chart(figd)

# creating Series page

if page =="Series":
    base_show=df_filtered[df_filtered.type=="TV Show"].drop_duplicates(subset=['cast'])
    numberofshows=base_show.show_id.nunique()
    totalnumberofcast=base_show.groupby('cast')['count_cast'].sum().reset_index()
    actorscount=totalnumberofcast.count_cast.sum()
    col1,col2=st.columns(2)
    col1.metric(" 📺  total number of shows",numberofshows)
    col2.metric("Total Number of Actors🎭", f"{actorscount}")

    df_filtered['count_cast']=df['cast'].apply(count_cast)
    actor_name = st.text_input("Add your favourite actor name: ",key="actor_input")
    show_name = st.text_input("Add your series name: ",key="series_inputt")
    showfilter=base_show.copy()
    if actor_name:
        showfilter = showfilter[showfilter['cast'].str.contains(actor_name, flags=re.IGNORECASE, na=False)]
    if show_name:
        showfilter=showfilter[showfilter['title'].str.contains(show_name, flags=re.IGNORECASE, na=False)]

    if actor_name and showfilter.empty:
        st.info(f"No results for actor: {actor_name}")

    elif actor_name:
        st.subheader(f"Titles with {actor_name}")
        st.dataframe(showfilter.drop_duplicates(subset=['description']))

    if show_name and showfilter.empty:
        st.info(f"No results for show: {show_name}")

    elif show_name:
        st.subheader(f"Search result for '{show_name}'")
        st.dataframe(showfilter.drop_duplicates(subset=['description']))

    # number of seasons distrubution

    showfilter.number_ofseasons=showfilter.number_ofseasons.astype('int64')
    figsh = px.histogram(showfilter, x='number_ofseasons', nbins=10, title='<b>Number of Seasons Distribution</b>', color_discrete_sequence=['red']).update_layout(title={'x':0.2})
    st.plotly_chart(figsh)
    # top 10 series genres
    genre_count = showfilter['category'].value_counts().reset_index().head(10)
    figs= px.bar(genre_count, x='category', y='count', title='<b>Top 10 series Genres</b>', color_discrete_sequence=['red']).update_layout(title={'x':0.5})
    st.plotly_chart(figs)

    # 10 series directors 
    top_directors = showfilter[showfilter['director']!='Not identified']
    top_directors=top_directors.director.value_counts().reset_index().head(10).sort_values(by='count',ascending=False)
    figsd = px.bar(top_directors, x='director', y='count', title='<b>Top 10 Series Directors</b>', color_discrete_sequence=['red']).update_layout(title={'x':0.5})
    st.plotly_chart(figsd)




