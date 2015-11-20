import requests
import os
from multiprocessing import Pool, Queue, Manager
from flask import Flask, url_for, render_template, json, send_from_directory, request

app = Flask(__name__, static_url_path='')

API_KEY="YOUR_API_KEY"

def get_image(resource, entity, article, queue):
    try:
        print "Image source: " + resource
        i_get_url = 'http://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&query=select+%3Fthumbnail+where+{+<'+resource+'>+dbo%3Athumbnail+%3Fthumbnail}&format=json&timeout=1000'
        i_results = requests.get(url=i_get_url)
        i_response = i_results.json()
        if i_response['results']['bindings']:
            picture = i_response['results']['bindings'][0]['thumbnail']['value']

            queue.put('<div class="Image_Wrapper" data-caption="'+entity['disambiguated']['name']+'"><a href="'+article['source']['enriched']['url']['url']+'" target="_blank"><img src="'+ picture+'" onerror="imgError(this);"/></a></div>')
    except Exception as e:
        print e


@app.route('/images')
def images():

    # Get URL parameters
    entity_arg = request.args.get('entity')
    subentity_arg = request.args.get('subentity')
    timespan_arg = request.args.get('timespan')
    sentiment_arg = request.args.get('sentiment')

    qSentiment = ""
    returnSentiment = ""
    #returnSentiment = "%2Cenriched.url.enrichedTitle.docSentiment.score"
    if sentiment_arg == "positive":
        qSentiment = "&q.enriched.url.enrichedTitle.docSentiment=|type=positive,score=>0.65|"
    elif sentiment_arg == "negative":
        qSentiment = "&q.enriched.url.enrichedTitle.docSentiment=|type=negative,score=<0.35|"

    print entity_arg
    imgTags=[]
    try:
        if entity_arg is None:
            subject_arg = request.args.get('subject')
            verb_arg = request.args.get('verb')
            object_arg = request.args.get('object')
            relationship = "&q.enriched.url.enrichedTitle=|relations.relation.subject.entities.entity.type=" + subject_arg + ",relations.relation.action.verb.text=" + verb_arg + ",relations.relation.object.entities.entity.type=" + object_arg + ",entities.entity.disambiguated.dbpedia=dbpedia|"
            get_url="https://access.alchemyapi.com/calls/data/GetNews?outputMode=json&start=now-" + timespan_arg + "d&end=now&count=25" + qSentiment + relationship +"&return=enriched.url.enrichedTitle.entities.entity.disambiguated%2Cenriched.url.title%2Cenriched.url.url%2Cenriched.url.enrichedTitle.entities.entity.type" + returnSentiment + "&apikey="+API_KEY
        else:
            search_type = "type=" + entity_arg
            if subentity_arg != "none":
                search_type += ",disambiguated.subType.subType_=" + subentity_arg
            query = "&q.enriched.url.enrichedTitle.entities.entity=|" +  search_type + ",disambiguated.dbpedia=dbpedia|"
            get_url="https://access.alchemyapi.com/calls/data/GetNews?outputMode=json&start=now-" + timespan_arg + "d&end=now&count=25" + qSentiment + query +"&return=enriched.url.enrichedTitle.entities.entity.disambiguated%2Cenriched.url.title%2Cenriched.url.url%2Cenriched.url.enrichedTitle.entities.entity.type" + returnSentiment + "&apikey="+API_KEY

        print "get_url: " + get_url

        results = requests.get(url=get_url)
        response = results.json()
        print "Initial response:"
        print response
    except Exception as e:
        print e

    entityList=[]

    l_pool = Pool(processes = 30)
    l_mgr  = Manager()
    l_resultQueue = l_mgr.Queue()

    i=0
    if 'result' in response:
        if 'docs' in response['result']:
            print "Items Found: " + `len(response['result']['docs'])`
            for article in response['result']['docs']:
                if 'source' in article and 'enriched' in article['source']:
                    for entity in article['source']['enriched']['url']['enrichedTitle']['entities']:
                        if (entity_arg != "person" or entity['type']=="Person"):
                            if 'disambiguated' in entity and 'dbpedia' in entity['disambiguated']:
                                if entity['disambiguated']['dbpedia']:
                                    resource=entity['disambiguated']['dbpedia']
                                    if resource not in entityList:
                                        entityList.append(resource)
                                        l_pool.apply_async(get_image, (resource, entity, article, l_resultQueue))

    l_pool.close()
    l_pool.join()

    while not l_resultQueue.empty():
        imgTags.append(l_resultQueue.get())

    images =  ''.join(imgTags)


    # Log Transactions Consumed
    print "\nNew transactions: " + response['totalTransactions']

    try:
        get_url="http://access.alchemyapi.com/calls/info/GetAPIKeyInfo?outputMode=json&apikey="+API_KEY
        results2 = requests.get(url=get_url)
        response2 = results2.json()
        print response2
        print "Transactions used this month: " + response2["consumedDailyTransactions"] + "\n"
    except Exception as e:
        print e

    return images


@app.route('/data/<path:path>')
def send_js(path):
    print "path: " + path
    return send_from_directory('static/data', path)

@app.route('/')
def main():
    return render_template('index.html')

port = os.getenv('VCAP_APP_PORT', '8000')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port), debug=True)
