from datetime import date as dt
from typing import Text
from transformers import AutoTokenizer, Trainer, TFAutoModelForSequenceClassification
import os
import tweepy
import boto3
os.environ["TOKENIZERS_PARALLELISM"] = "true"

class Twitter:
    #Creates tweepy object to call twitter api
    auth = tweepy.OAuthHandler(['consumer_key'],['consumer_secret'])
    auth.set_access_token(['access_token'], ['access_token_secret'])
    api_tweety = tweepy.API(auth)
    
    def get_tweets(self,keyword):
        '''
        Function to get at most 100 tweets with the included keyword
        
        arguement:
            keyword - A string of up to 150 characters.
        returns:
            tweepy response object
        '''
        return self.api_tweety.search(q=keyword, count=100)

class Roberta:
    # Create class for data preparation
    class SimpleDataset:
        def __init__(self, tokenized_texts):
            self.tokenized_texts = tokenized_texts
        
        def __len__(self):
            return len(self.tokenized_texts["input_ids"])
        
        def __getitem__(self, idx):
            return {k: v[idx] for k, v in self.tokenized_texts.items()}
    
    def prepare_models(self):
        model_name = "siebert/sentiment-roberta-large-english"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = TFAutoModelForSequenceClassification.from_pretrained(model_name)
        trainer = Trainer(model=model)
        
        return tokenizer, trainer

    def predict(self, pred_texts, tokenizer, trainer):
        tokenized_texts = tokenizer(pred_texts,truncation=True,padding=True)
        pred_dataset = self.SimpleDataset(tokenized_texts)
        predictions = trainer.predict(pred_dataset)
        
        #0=negative 1=positive
        predictions = predictions.predictions.argmax(-1)
        
        return predictions
    
    def roberta_run(self, pred_texts):
        tokenizer, trainer = self.prepare_models()
        return self.predict(pred_texts, tokenizer, trainer)

class AWS:
    def add_data(self, telecom_data):
        date = str(dt.today())
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('telecom_twitter_sentiment')
        item = {'data':date,'text_item':telecom_data}
        table.put_item(Item=item)

class RunProgram:
    def run(self):
        telecom_companies = ['#comcast', '#fios', '#cox']
        
        telecom_analysis = {}
        for company in telecom_companies:
            tweets = Twitter().get_tweets(company)
            tweet_text = [tweet._json['text'] for tweet in tweets]
            preds = Roberta().roberta_run(tweet_text)
            positive = int(sum(preds))
            negative = len(preds) - positive 
            telecom_analysis.update({company:[positive, negative]})
            
        AWS().add_data(telecom_analysis)
        
if __name__ == '__main__':
    RunProgram().run()