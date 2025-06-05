import pandas as pd
import streamlit as st
import plotly.express as px
import re
import base64

## Reading files
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
    df_filtered['year_added'] = df_filtered.date_added.dt.year
    yearadded = df_filtered.groupby('year_added')['show_id'].count().reset_index()
    user_theme = st.get_option("theme.base")
    if user_theme == 'light':
        font_color = 'black'
        bg_color = 'white'
        bar_color = 'red'
        line_color = 'red'
        pie_colors = {'Movie': 'red', 'TV Show': '#000000'}  # black for TV Show
        grid_color = '#ddd'
        type_colors = {'Movie': 'red', 'TV Show': 'black'}
        legend_style = dict(
            font=dict(color=font_color, family='Arial', size=14),
            bgcolor=bg_color,
            bordercolor=font_color,
            borderwidth=1)
        title_fonnt = dict(size=20, color=font_color, family='Arial', weight='bold')

    else:
        font_color = 'white'
        bg_color = '#111111'
        line_color = 'red'
        bar_color = 'red'
        pie_colors = {'Movie': 'red', 'TV Show': 'white'}
        grid_color = '#444'
        type_colors = {'Movie': 'red', 'TV Show': 'white'}
        legend_style = dict(
            font=dict(color=font_color, family='Arial', size=14),
            bgcolor=bg_color,
            bordercolor=font_color,
            borderwidth=1)
        title_fonnt= dict(size=20, color=font_color, family='Arial', weight='bold')

    # Pie chart showing Distrubution
    fig_type = px.pie(distrubuttion,names='type',values='show_id',title='Netflix Distribution: Movies vs Shows',color_discrete_map=pie_colors,color='type')
    fig_type.update_layout(plot_bgcolor=bg_color,paper_bgcolor=bg_color,title={'text': 'Netflix Distribution: Movies vs Shows','x': 0.2,'font': {'size': 20, 'color': font_color, 'family': 'Arial'}},    font=dict(color=font_color, family='Arial'),legend=legend_style)
    fig_type.update_traces(textfont=dict(family='Arial', size=14, color=font_color), textinfo='label+percent+value')
    st.plotly_chart(fig_type, use_container_width=True)

    # Top 10 common genres bar chart
    genres = df.groupby('category')['show_id'].count().reset_index()
    genres.sort_values(by='show_id', ascending=False, inplace=True)
    top_genres = genres.head(10)
    fig_genres = px.bar(top_genres,x='category',y='show_id',title='10 Top Common Genres',text_auto=True,color_discrete_sequence=[bar_color])
    fig_genres.update_layout(plot_bgcolor=bg_color,paper_bgcolor=bg_color,yaxis_title='Count of genre',xaxis_title='Category',title={'x': 0.3, 'font': {'size': 20, 'color': font_color, 'family': 'Arial'}},font=dict(color=font_color, family='Arial'))
    fig_genres.update_xaxes(tickfont=dict(family='Arial', size=14, color=font_color))
    fig_genres.update_yaxes(tickfont=dict(family='Arial', size=14, color=font_color))
    st.plotly_chart(fig_genres, use_container_width=True)

    # Top countries producing Netflix content bar chart
    countries = df.groupby('new')['show_id'].count().reset_index()
    countries.sort_values(by='show_id', ascending=False, inplace=True)
    top_countries = countries.head(10)
    fig_countries = px.bar(top_countries,x='new',y='show_id',title='What are the top countries producing Netflix content?',text_auto=True,color_discrete_sequence=[bar_color])
    fig_countries.update_layout(plot_bgcolor=bg_color,paper_bgcolor=bg_color,yaxis_title='Count of content',xaxis_title='Country Name',title={'x': 0.2, 'font': {'size': 20, 'color': font_color, 'family': 'Arial'}},font=dict(color=font_color, family='Arial'),xaxis=dict(tickfont=dict(family='Arial', size=14, color=font_color)),yaxis=dict(tickfont=dict(family='Arial', size=14, color=font_color)))
    st.plotly_chart(fig_countries, use_container_width=True)
    # total content volume over years

    figy = px.line(data_frame=yearadded,x='year_added',y='show_id',title="How has Netflix's content volume changed over time?",color_discrete_sequence=[line_color])
    figy.update_layout(plot_bgcolor=bg_color,paper_bgcolor=bg_color,font=dict(color=font_color, family='Arial', size=14),title=dict(font=dict(size=20, color=font_color, family='Arial',), x=0.2),xaxis=dict(title='Year Added',tickmode='linear',tickfont=dict(family='Arial', size=14, color=font_color),gridcolor=grid_color),yaxis=dict(title='Count of Content',tickfont=dict(family='Arial', size=14, color=font_color),gridcolor=grid_color))
    st.plotly_chart(figy, use_container_width=True)
    # content count by type over years

    typeandyear = df_filtered.groupby(['type', 'year_added'])['show_id'].count().reset_index()
    type_year = px.line(data_frame=typeandyear,x='year_added',y='show_id',color='type',title='Are TV shows becoming more common than movies?',color_discrete_map=type_colors)

    type_year.update_layout(
        width=1000,
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=font_color, family='Arial', size=14),
        title=dict(text='Are TV shows becoming more common than movies?', x=0.3, font=dict(color=font_color, family='Arial', size=18)),
        legend=legend_style,
        xaxis=dict(
            title='Year Added',
            tickfont=dict(color=font_color, family='Arial', size=14),
            title_font=title_fonnt,
            gridcolor=grid_color,
            tickmode='linear'
        ),
        yaxis=dict(
            title='Count of Content',
            tickfont=dict(color=font_color, family='Arial', size=14),
            title_font=title_fonnt,
            gridcolor=grid_color ))

    st.plotly_chart(type_year, use_container_width=True)
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




