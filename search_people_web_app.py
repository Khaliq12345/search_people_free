from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from requests import session
ses = session()
import numpy as np

st.set_page_config(page_title= 'searchpeoplefree.com scraper', page_icon=":smile:")
hide_menu = """
<style>
#MainMenu {
    visibility:hidden;}
footer {
    visibility:hidden;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

def format_text(text):
    text = text.lower()

    # Replace spaces with hyphens
    text = text.replace(" ", "-")

    # Remove dots
    text = text.replace(".", "")

    return text

def scraper():
    n = 0
    item_list = []
    API_KEY = api
    col1, col2 = st.columns(2)
    progress = col1.metric('Data scraped', 0)
    item_list = []
    for x, y, z, s, c in zip(fn, mn, ln, states, cities):
        n = n + 1
        name = f'{x} {y} {z}'
        name = name.replace('nan ', '')
        f_name = format_text(name)
        state = format_text(s)
        city = format_text(c)

        link = f'https://www.searchpeoplefree.com/find/{f_name}/{state}/{city}'

        payload = {'api_key': API_KEY, 'url':f'{link}', 'dynamic':'false'}
        resp = ses.get('https://api.scrapingdog.com/scrape', params=payload)
        soup = BeautifulSoup(resp.text, 'lxml')
        progress.metric('Data scraped', value=n)

        cards = soup.select('li.toc.l-i.mb-5') # Only save the box with 'MD'
        new_card = []
        for card in cards:
            if f'{keyword}' in card.select_one('.h2').text:
                new_card.append(card)
            else:
                pass
        
        if len(new_card) < 1:
            name_box = 'Not found'
        else:
            for new in new_card: # Only save the box with specified and name and last name
                text = new.select_one('.h2').text.split(',')
                text = text[0]

                if f'{x}' in text and f'{z}' in text:
                    name_box = new
                    break
                else:
                    name_box = new_card[0]
        
        try:
            try:
                address = name_box.select_one('address a').text
            except:
                address = name_box.select_one('.col-lg-6 span').text
        except:
            address = 'Not found'

        try:
            phone = name_box.select_one('h4 a').text
        except:
            phone = 'Not found'
        
        items = {
            'Name': name,
            'Address': address,
            'Phone': phone
        }
        item_list.append(items)

    df = pd.DataFrame(item_list)
    st.dataframe(df)
    col2.metric('Total data scraped', value=len(df))
    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='searchpeople-names.csv',
    mime='text/csv',
    )


st.title('SEARCHPEOPLE FREE SCRAPER')
st.caption('This web app will compare names scraped from legacy.com with searchpeoplefree.com')
st.caption('Upload file that was scraped directly from the legacy.com, any modification to the csv file can cause an error in this web app')
api = st.text_input('Your scrapingdog api key', placeholder='621b03gths82760235d2259d0')
keyword = st.text_input('The state', placeholder= 'MD')
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    fn = df['First Name'].to_list()
    ln = df['Last Name'].to_list()
    mn = df['Middle Name'].to_list()
    cities = df['City'].to_list()
    states = df['State'].to_list()
    city = [df['State'].max() if x is np.nan else x for x in cities]
    state = [df['State'].max() if x is np.nan else x for x in states]

button = st.button('Scrape!')

if button:
    scraper()
    st.balloons()
    st.success('Done!')
