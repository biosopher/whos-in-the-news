## Advanced Who's in the News
Check out the [demo running on Bluemix](http://whos-in-the-news-advanced.mybluemix.net) to experience what you can build.

This code base builds off the original source at ["Who's in the News" by Zach Walchuk](https://developer.ibm.com/watson/blog/2015/05/11/whos-in-the-news-an-alchemydata-news-application/).  We still use the majority of Zach's code to obtain the latest new from AlchemyData News.  But we now provide users a quick drop down of to filter by Alchemy-defined entity or subentity.

[![](wiki/media/demo_screenshot.png)](http://ipa-demo-anthony.mybluemix.net/)


#### Getting Started
Once you have the files, enter your API key in newsApp.py under the API_KEY variable. To kick things off:

```
cd whos-in-the-news
python newsApp.py
```
After that, access the application locally at port 8000: [http://localhost:8000](http://localhost:8000). 

#### Track your Transactions
Monitor your remaining transactions carefully.  Each API call typically consumes >1 transaction.  E.g. a query for News about people that are actors for 7 days might cost 25 transaction.  And asking that same query over 28 days could costs 4x as much.  So be careful and make each query over a limited # of days to start.

Check your remaning transactions with this query.  `Replace <api_key> with your api key.`:
```
curl -i http://access.alchemyapi.com/calls/info/GetAPIKeyInfo?apikey=<api_key>
```
You'll receive your daily usage plus transaction limit in the returned xml:
```
<?xml version="1.0" encoding="UTF-8"?>
<results>
    <status>OK</status>
    <consumedDailyTransactions>0</consumedDailyTransactions>
    <dailyTransactionLimit>100000</dailyTransactionLimit>
</results>
```






