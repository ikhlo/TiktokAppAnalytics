import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from wordcloud import WordCloud
from utils import build_word_cloud, author_count_activity
from tiktok import get_data

import sys
import os
import subprocess
from subprocess import call, run, Popen

import streamlit as st
st.set_page_config(layout="wide")

# Create a sidebar
style_str = 'display:inline-block;text-align:center; vertical-align:middle;'
st.sidebar.markdown(f"<div><img \
    src='https://pngshare.com/wp-content/uploads/2021/05/Tik-Tok-Logo-Wallpaper-17.png'\
    width=100 /><h1 style='{style_str}'>Unofficial <br> TikTok Analytics</h1></div>",
                    unsafe_allow_html=True)
st.sidebar.markdown(
    "This interactive dashboard allows you to analyse tiktok trendings in real time very easily. 📈")
st.sidebar.markdown("How to use it ? \
    <ol><li>Enter the hashtag you want to analyse.</li>\
    <li>Press **Get Data** button.</li>\
    <li>Analyze the visualizations.</li></ol>", unsafe_allow_html=True)


@st.cache
def convert_df(dataframe):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return dataframe.to_csv().encode('utf-8')


# Search bar
st.title('Tiktok Analytics Dashboard')
with st.form(key='my_form'):
    text, int_val, int_val2, _ = st.columns([3, 2.6, 2.6, 2])
    hashtag = text.text_input(
        'Search for a hashtag here', placeholder="Type any hashtag as fifa, f1, ...")
    nb_results = int_val.number_input('Amount of data to fetch', min_value=20,
                                      max_value=1000, value=50, step=10)
    nb_words = int_val2.number_input('Number of common hashtags', min_value=10,
                                     max_value=30, value=20, step=1)
    submit_button = st.form_submit_button('Get Data')

# Rename columns of dataframe
rename_columns = {'stats_diggCount':'NbOfLikes', 'stats_playCount':'NbOfViews',
'stats_shareCount':'NbOfShares', 'stats_commentCount':'NbOfComments',
'authorStats_videoCount': 'author_NbOfVideos', 'authorStats_heartCount':'author_NbOfLikes',
'authorStats_followerCount': 'author_NbOfFollowers'}

if submit_button:
    st.header(f"Analysis of '{hashtag}' hashtag.")
    # Fetch data
    st.write(f"{sys.executable}")
    Popen([f"{sys.executable} tiktok.py {hashtag} {nb_results}"]).wait()
    #call([f"{sys.executable}",'tiktok.py', hashtag, str(nb_results)])

    df = pd.read_csv(os.path.dirname(__file__) +'/tiktokData.csv', index_col=0)
    df = df.rename(columns=rename_columns)
    df['trunc_desc'] = df['desc'].apply(
        lambda x: x[:30]+'...' if len(x) > 30 else x)

    # Histogram viz
    fig = px.bar(df.sort_values(
        by=['NbOfLikes'],
        ascending=False
    ).head(5).sort_values(['NbOfLikes']),
        x='NbOfLikes', y='trunc_desc',
        hover_data={'trunc_desc': False, 'desc': True, 'author_nickname':True},
        orientation='h', height=400, color_discrete_sequence=["#69c9d0"]*len(df))
    fig.update_layout(
        title="The 5 most liked videos",
        xaxis_title="Count of Likes",
        yaxis_title="Videos description",
        title_x=0.5,
        title_font_family="Arial Black",
        font=dict(
            size=15,
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # Split page into two columns
    left_col, right_col = st.columns(2)

    # Video viz
    scatter1 = px.scatter(df,
                          x='NbOfViews', y='NbOfShares',
                          size='NbOfComments', color='NbOfComments',
                          hover_data=['desc'])
    scatter1.update_layout(
        title="Videos analysis",
        xaxis_title="Count of views",
        yaxis_title="Count of shares",
        title_x=0.5,
        title_font_family="Arial Black",
    )
    scatter1.layout.coloraxis.colorbar.title = "Count of comments"
    left_col.plotly_chart(scatter1, use_container_width=True)

    # Author viz
    scatter2 = px.scatter(df, x='author_NbOfVideos',
                          y='author_NbOfLikes',
                          size='author_NbOfFollowers',
                          color='author_NbOfFollowers',
                          hover_data=['author_nickname'])
    scatter2.update_layout(
        title="Authors analysis",
        xaxis_title="Number of posted videos",
        yaxis_title="Count of sharing",
        title_x=0.5,
        title_font_family="Arial Black",
    )
    scatter1.layout.coloraxis.colorbar.title = "Number of followers"
    right_col.plotly_chart(scatter2, use_container_width=True)

    most1, most2 = st.columns(2)
    # Word cloud to see most common hashtags
    with most1:
        st.markdown(
            "<h4 style='text-align:center'>Most common hashtags</h4>", unsafe_allow_html=True)
        wordcloud_viz = WordCloud(background_color='white',
                                  width=780,
                                  height=560).generate_from_frequencies(build_word_cloud(df, hashtag, nb_words))
        plt.imshow(wordcloud_viz, interpolation="bilinear")
        plt.axis('off')
        plt.savefig('wordcloud.png')
        st.image(os.path.dirname(__file__) +'/wordcloud.png', use_column_width='auto', )

    with most2:
        sub_df = author_count_activity(df)
        fig2 = px.bar(sub_df,
            x='author_nickname', y='activity',
            hover_data={'activity': True, 'author_nickname' : False, 
            'video_mean_duration': True, 'sum_of_likes':True, 'signature':True},
            height=500, color_discrete_sequence=['#ee1d52']*len(df))
        fig2.update_layout(
            title="The 5 most active authors",
            xaxis_title="Tiktok account",
            yaxis_title="Videos with this hashtag",
            title_x=0.5,
            title_font_family="Arial Black",
            font=dict(
                size=15,
            )
        )
        st.plotly_chart(fig2, use_container_width=True)

    # The dataframe
    st.header('The complete dataframe')
    st.download_button(
        label="Download data as CSV",
        data=convert_df(df),
        file_name=f'tiktokData_{hashtag}.csv',
        mime='text/csv',
    )
    df
