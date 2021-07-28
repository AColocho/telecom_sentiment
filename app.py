import streamlit as st
import matplotlib.pyplot as plt
import boto3
from datetime import date, timedelta

def get_data():
    data = []
    for day in range(0,7):
        data_date = str(date.today() - timedelta(day))
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(st.secrets['AWS_TABLE'])
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
                x.append(str(date.today() - timedelta(value)))
                
        col.bar(x,data)
        col.set_yticks(range(1))
        col.set_ylabel('Positive Tweet Percentage')
        col.title.set_text(title)
        col.tick_params(axis='x', labelrotation=45)
        i += 1

'''
# Telecommunication Company Tweet Sentiment

At most 100 tweets* related to each company are extracted from twitter daily, and they are ran through a machine learning model to detect sentiment.
The measure shown in the charts below are the percentage of positive tweets from all the tweets extracted.
The model used to identitdy sentiment is sentiment-roberta-large-english. More info about the model can be found in this paper [More than a feeling: Benchmarks for sentiment analysis accuracy](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3489963).
The source code to this app can be found [here](https://github.com/AColocho/telecom_sentiment)

* Sometimes less than 100 tweets are availible for extraction due to unkown reasons related to the twitter API.
'''

st.pyplot(fig)