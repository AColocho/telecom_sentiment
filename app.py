import streamlit as st
import matplotlib.pyplot as plt
import boto3
from datetime import date, timedelta

def get_data():
    data = []
    for day in range(0,7):
        data_date = str(date.today() - timedelta(day))
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('telecom_twitter_sentiment')
        response = table.get_item(Key={'data':data_date})
        try:
            text_item = response['Item']['text_item']
            data.append(text_item)
        except:
            pass
    
    return data

def prep_data(data):
    companies = ['#comcast','#fios','#cox']
    
    company_data = {}
    for company in companies:
        temp_data = []
        for i in data:
            total = sum(i.get(company))
            postive_perct = i.get(company)[0]/total
            temp_data.append(postive_perct)
            
        company_data.update({company:temp_data})
    
    return company_data

data = get_data()
clean_data = prep_data(data)
comparison_data = [clean_data.get(company)[0] for company in clean_data.keys()]
ordered_data = [comparison_data, clean_data.get('#comcast'), clean_data.get('#fios'), clean_data.get('#cox')]
titles = ['Daily Comparison', 'Comcast', 'Fios', 'Cox']
fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(10,10))
fig.subplots_adjust(hspace=.3, wspace=.5)
i = 0
for row in ax:
    for col in row:
        title = titles[i]
        data = ordered_data[i]
        
        if 'Comparison' in title:
            x = ['Comcast', 'Fios', 'Cox']
        else:
            x = []
            for value in range(0,len(data)):
                x.append(date.today() - timedelta(value))
                
        col.bar(x,data)
        col.set_ylabel('Positive Tweet Percentage')
        col.title.set_text(title)
        col.tick_params(axis='x', labelrotation=45)
        i += 1

'''
# Telecommunication Company Tweet Sentiment

100 tweets are extracted from the twitter API daily and processed through machine learning to detect sentiment.
The model used to identitdy sentiment is sentiment-roberta-large-english. More info about the model can be found in this paper [More than a feeling: Benchmarks for sentiment analysis accuracy](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3489963).
The source code to this app can be found [here](https://github.com/AColocho/telecom_sentiment)
'''

st.pyplot(fig)