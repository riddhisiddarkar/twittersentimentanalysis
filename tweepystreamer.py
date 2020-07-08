from tweepy import API
#Cursor is class that allows us to get user timeline tweets
from tweepy import Cursor
#class from tweepy module that will help us to listen to the tweets coming from the api
from tweepy.streaming import StreamListener
#class which will help us to authenticate based on the credentials
from tweepy import OAuthHandler
from tweepy import Stream
#import the twitter credentials
import twitter_credentials
#importing numpy
import numpy as np
#importing pandas
import pandas as pd
#import matplotlib
import matplotlib.pyplot as plt
#to access your timeline as well as someones timeline
#importing textblob
from textblob import TextBlob
#importing regular expression
import re
#function to count the no of positive,negative and neutral tweets
def classifytweets(sentiments):
        positive=0
        negative=0
        neutral=0
        for sentiment in sentiments:
            if(sentiment==1):
                positive=positive+1
            elif(sentiment==-1):
                negative=negative+1
            else:
                neutral=neutral+1
        return positive,negative,neutral
class TwitterClient():
    #user=>the user whose timeline tweets u want to access.By default we assign it to none
    def __init__(self,user=None):
        self.auth=TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client=API(self.auth)
        self.user=user

    def get_twitter_client_api(self):
        return self.twitter_client
    #function to get tweets
    #num_tweets=>allows us to determine how many tweets are needed
    def get_user_tweets(self,num_tweets):
        tweets=[]
        #loop through the tweets and store in the list
        #from the API method each object has a property that helps us to get the timeline of the user specified
        #if user is not specified then it gets the developers own timeline.By default it is null and specifies the user
        #the items tells how many tweets should be given frim the timeline
        #id=>tells which user you want to access
        for tweet in Cursor(self.twitter_client.user_timeline,id=self.user).items(num_tweets):
            tweets.append(tweet)
        return tweets
        #to determin the no of friend
    def get_tweets_as_hastags(self,hashtag,num_tweets):
        tweets=[]
        for tweet in Cursor(self.twitter_client.search,q=hashtag).items(num_tweets):
            tweets.append(tweet)
        return tweets
#class for authentication
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        #authenticating using the credentails
        auth=OAuthHandler(twitter_credentials.CONSUMER_KEY,twitter_credentials.CONSUMER_SECRET)
        #to complete the authenticate
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN,twitter_credentials.ACCESS_TOKEN_SECRET)
        #returns the auth
        return auth
#class responsible for streaming and processing the tweets
class TwitterStreamer():
        #handles the authentication and the connection with the twitter streaming api
        #make a constructor to authenticate
    def __init__(self):
        self.twitterauthenticator=TwitterAuthenticator()
    #fetched_tweets_filename=>is the name of the file where the data from the tweets is stored
    #hast_tag_list=>all the hastags that are filtered as per occurence
    def stream_tweets(self,fetched_tweets_filename,hash_tag_list):
        # create an object of the TwitterListner
        listener=TwitterListner(fetched_tweets_filename)
        #gets the auth here
        auth=self.twitterauthenticator.authenticate_twitter_app()
        #after authentication now we create a stream
        stream=Stream(auth,listener)
        #filtering the tweets focusing on keywords,hashtags
        stream.filter(track=hash_tag_list)

#class to print the recieved tweets
class TwitterListner(StreamListener):
    #creating a constructor and the storing the name of the file where the tweets are to be stored
    def __init__(self,fetched_tweets_filename):
        self.fetched_tweets_filename=fetched_tweets_filename  
    def on_data(self,data):
        #trying to  catch any errors
        try:
            #u get a json formatted dictionary object
            #opens the file and appends the tweets
            with open(self.fetched_tweets_filename,'a') as tf:
                tf.write(data)
            #to ensure all went correctly we return true
            return True
        #catches the errors
        except BaseException as e:
            print("here is the error")
    #if there is an error in the streamlistener class this is called
    def on_error(self,status):
        #if twitter is abusing their sysytem.then there is a window so we need to check and then not get thrown out
        if status==420:
            return False
        #print the error
        print(status)
#class to analyze the tweets
class TweetAnalyzer():
    #to clean the tweet
    def clean_tweet(self,tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())        
    #analysing the sentiment of the tweet
    def analyze_sentiment(self,tweet):
        analysis=TextBlob(self.clean_tweet(tweet))
        #polarity tells us if the tweet is positive or negative
        if analysis.sentiment.polarity>0:
            return 1
        elif analysis.sentiment.polarity==0:
            return 0
        else:
            return -1
    #extracting tweet text from tweets
    # helps to show the user the data
    def convert_tweet_to_df(self,tweets):
        #columns='Tweets' specifies the name of the column they are stored in
        df=pd.DataFrame(data=[tweet.text for tweet in tweets],columns=["Tweets"])
        #to store all the ids in an array
        df['id']=np.array([tweet.id for tweet in tweets])
        #to get the length of each tweet
        df['length']=np.array([len(tweet.text) for tweet in tweets])
        #to get the date when it was tweeted
        df['date']=np.array([tweet.created_at for tweet in tweets])
        #to get the source of the tweet
        df['source']=np.array([tweet.source for tweet in tweets])
        #get the no of likes on a tweet
        df['likes']=np.array([tweet.favorite_count for tweet in tweets])
        #to get the no of retweets
        df['retweets']=np.array([tweet.retweet_count for tweet in tweets])
        return df
    #makes the piechart
    def makepiechart(self,sentiments):
        #calls the classify tweet function to get the no of positive,negative nad neutral tweets
        positive,negative,neutral=classifytweets(sentiments)
        #assign the labels
        labels=['Positive','Negative','Neutral']
        #makes an array of the no of positive,negative and neutral
        sizes=[positive,negative,neutral]
        #colors to be used in the piechart
        colors=['gold','lightskyblue','lightcoral']
        #which parts of the pie should come out
        explode=(0.1,0.1,0)
        #sets the data,which part should be out,colors
        #also tells how the show the total data,show the shadow and sets the start angle to 90deg
        plt.pie(sizes,explode=explode,labels=labels,colors=colors,autopct='%1.1f%%',shadow=True,startangle=140)
        plt.axis('equal')
        #shows the plot
        plt.show()
    #function to make a bargraph    
    def make_bargraph(self,sentiments):
        #calls the classify tweet function to get the no of positive,negative nad neutral tweets
        positive,negative,neutral=classifytweets(sentiments)
        #the labels
        sentiment=('Positive','Negative','Neutral')
        y_pos=np.arange(len(sentiment))
        #the values
        nos=[positive,negative,neutral]
        #the data to plot the bar graph
        plt.bar(y_pos,nos)
        #sets the y-label
        plt.ylabel("No of tweets")
        #sets the title of the bargraph
        plt.title("Sentiment analysis")
        #shows the title of the bargraph
        plt.show()
if __name__ == "__main__":
    # create a TweetAnalyzer
    tweet_analyzer=TweetAnalyzer()
    #create a TwitterClient
    twitter_client=TwitterClient()
    #continous loop till user wants to exit
    while True:
        print("What do you want to analyze?")
        print("Analze tweets by a hashtag.Enter 1")
        print("Analyze tweets of a particular indivisual.Enter 2")
        print("Exit 3")
        n=int(input())
        if (n==1):
            hashtag=input("Enter the hashtag to analyze:-\t")
            print(hashtag)
            #try checks if anything else other than a no is entered
            try:
                no=int(input("Enter the no of hashtags you want to analyze:-\t"))
            except:
                print("Invalid no entered\nOperation aborted\n")
                #cancels the current iteration
                continue
            print(no)
            #if the no is less than one than leave the current iteration
            if(no<1):
                continue
            ts=twitter_client.get_tweets_as_hastags(hashtag,no)
            #if the api returns an empty array
            if(ts==[]):
                print("No such hashtag found")
                continue
            tweet_df=tweet_analyzer.convert_tweet_to_df(ts)
            #sets the dataframe column to get the sentiment
            tweet_df['sentiment']=np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in tweet_df['Tweets']])
            print(tweet_df)
            #makes an array of the sentiment column of the dataframe
            sentiments=np.array(tweet_df['sentiment'])
            n=0
            #takes in input for how to display the analysed data.ie in a bar graph,pie chart or both
            #iterates till you get the correct response
            while(n!=1 and n!=2 and n!=3):
                print("How do you want to visualize the data")
                print("As a bar graph.Enter 1")
                print("As a pie chart.Enter 2")
                print("Both as a bar graph and pie chart.Enter 3")
                n=int(input("enter your choice:-\t"))
            if(n==1):
                tweet_analyzer.make_bargraph(sentiments)
            elif(n==2):
                tweet_analyzer.makepiechart(sentiments)
            elif(n==3):
                tweet_analyzer.make_bargraph(sentiments)
                tweet_analyzer.makepiechart(sentiments)
        elif n==2:
            username=input("Enter the correct user name\neg for To analze Donald Trump enter his userid ie realDonald.\t")
            print(username)
            #checks if the input is a number
            try:
                no=int(input("Enter the no of hashtags you want to analyze:-\t"))
            except:
                #if not a no then skips the current iteration
                print("Invalid no entered\nOperation aborted")
                continue
            #if the no is less than 1 then we skip the iteration
            if(no<1):
                continue
            api=twitter_client.get_twitter_client_api()
            #user_timeline is a function provided from the twitter client api
            #screen name is the name of the person whose tweets we want to get
            #count tells the no of tweets you want
            #count and screen_name are variables from the documentation and we cannot change them
            try:
                tweets=api.user_timeline(screen_name=username,count=no)
            except:
                print("unauthorised access")
                continue
            #if the api returns an empty arrat
            if(tweets==[]):
                print("Either such a user doesnot exist else he has not tweeted yet")
                continue
            #converts the tweets to a dataframe so its easier to display the data
            tweet_df=tweet_analyzer.convert_tweet_to_df(tweets)
            #sets a column of sentiment in the dataframe by analyaing the tweet text
            tweet_df['sentiment']=np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in tweet_df['Tweets']])
            print(tweet_df)
            #makes an numpy array of the the sentiment column of the dataframe
            sentiments=np.array(tweet_df['sentiment'])
            n=0
            #takes in input for how to display the analysed data.ie in a bar graph,pie chart or both
            #iterates till you get the correct response
            while(n!=1 and n!=2 and n!=3):
                print("How do you want to visualize the data")
                print("As a bar graph.Enter 1")
                print("As a pie chart.Enter 2")
                print("Both as bar graph and pie chart.Enter 3")
                n=int(input("Enter your choice:-\t"))
            if(n==1):
                tweet_analyzer.make_bargraph(sentiments)
            elif(n==2):
                tweet_analyzer.makepiechart(sentiments)
            elif(n==3):
                tweet_analyzer.make_bargraph(sentiments)
                tweet_analyzer.makepiechart(sentiments)
        elif n==3:
            #exits the loop and program
            break
        else:
            #invalid input.Try agian
            print("Please enter a valid input")
#end of program