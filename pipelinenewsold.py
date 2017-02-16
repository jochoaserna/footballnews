# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#NUEVAS ORDENES

#SENTIMENTS
#$ python pipelinenews.py Elasticsearch --filename footballnews --analysis sentiments --index footballnews --doc-type sentiments --local-scheduler

#EMOTIONS
#$ python pipelinenews.py Elasticsearch --filename footballnews-emo --analysis emotions --index footballnews-emo --doc-type emotions --local-scheduler


import datetime
import json
import random
import requests



import luigi
from luigi.contrib.esindex import CopyToIndex

class FetchDataTask(luigi.Task):
    """
    Generates a local file containing 5 elements of data in JSON format.
    """

    #: the date parameter.
    #date = luigi.DateParameter(default=datetime.date.today())
    filename = luigi.Parameter()
    analysis = luigi.Parameter()

    #field = str(random.randint(0,10000)) + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    def run(self):
        """
        Writes data in JSON format into the task's output target.
        The data objects have the following attributes:
        * `_id` is the default Elasticsearch id field,
        * `text`: the text,
        * `date`: the day when the data was created.
        """
        #today = datetime.date.today()
        file = "analysis/"+self.filename

        with open(file) as f:
            j = json.load(f)
    		#for i in j:
    			#i["_id"] = i["id"]
      
        with self.output().open('w') as output:
            json.dump(j, output)
            output.write('\n')

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi.LocalTarget(path='analysis/%s.json' % self.filename)

class SenpyTask(luigi.Task):
    """
    This task loads data fetched with previous task and send it to Senpy tool in order to analyze 
    data retrieved and check sentiments expressed.
    """
    #: date task parameter (default = today)
    #date = luigi.DateParameter(default=datetime.date.today())
    filename = luigi.Parameter()
    analysis = luigi.Parameter(default='sentiments')

    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.FetchDataTask`
        :return: object (:py:class:`luigi.task.Task`)
        """
        return FetchDataTask(self.filename,self.analysis)

    def output(self):
        """
    	Returns the target output for this task.
            In this case, a successful execution of this task will create a file on the local filesystem.
            :return: the target output for this task.
            :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi.LocalTarget(path='analysis/analyzed-%s.jsonld' % self.filename)	

    def run(self):
        """
        Send data to Senpy tool and retrieve it analyzed. Store data in a json file.
        """
        with self.output().open('w') as output:
            with self.input().open('r') as infile:
                j = json.load(infile)
                #reviews = j['reviews']
                if(self.analysis == 'sentiments'):
                    #for i in reviews:
                    for i in j:
                        #r = requests.get('http://senpy.cluster.gsi.dit.upm.es/api/?algo=sentiText&language=es&i=%s' % i["text"])
                        r = requests.post("http://senpy.cluster.gsi.dit.upm.es/api/", data={'input': i["articleBody"], 'algo': 'sentiText', 'language': 'es'})
                        response = r.content.decode('utf-8')
                        response_json = json.loads(response)
                        print(response_json)
                        #i["sentimentAnalysis"] = response_json			
                        i["sentiment"] = response_json["entries"][0]["sentiments"][0]["marl:hasPolarity"]   
                        i["polarity"] = response_json["entries"][0]["sentiments"][0]["marl:polarityValue"]
                        output.write(json.dumps(i))
                        output.write('\n')

                if(self.analysis == 'emotions'):
                    #for i in reviews:
                    for i in j:
                        #r = requests.get('http://senpy.cluster.gsi.dit.upm.es/api/?algo=EmoTextANEW&language=es&i=%s' % i["text"])
                        r = requests.post("http://senpy.cluster.gsi.dit.upm.es/api/", data={'input': i["articleBody"], 'algo': 'EmoTextANEW', 'language': 'es'})
                        response = r.content.decode('utf-8')
                        response_json = json.loads(response)
                        #i["emotionAnalysis"] = response_json

                        emo = response_json["entries"][0]["emotions"][0]["onyx:hasEmotion"][0]["onyx:hasEmotionCategory"].split("#")
                        i["emotion"] = emo[1]
                        output.write(json.dumps(i))
                        output.write('\n')

class Elasticsearch(CopyToIndex):
    """
    This task loads JSON data contained in a :py:class:`luigi.target.Target` into an ElasticSearch index.
    This task's input will the target returned by :py:meth:`~.Senpy.output`.
    This class uses :py:meth:`luigi.contrib.esindex.CopyToIndex.run`.
    After running this task you can run:
    .. code-block:: console
        $ curl "localhost:9200/example_index/_search?pretty"
    to see the indexed documents.
    To see the update log, run
    .. code-block:: console
        $ curl "localhost:9200/update_log/_search?q=target_index:example_index&pretty"
    To cleanup both indexes run:
    .. code-block:: console
        $ curl -XDELETE "localhost:9200/example_index"	
        $ curl -XDELETE "localhost:9200/update_log/_query?q=target_index:example_index"
    """

    filename = luigi.Parameter()
    analysis = luigi.Parameter()

    #: date task parameter (default = today)
    date = luigi.DateParameter(default=datetime.date.today())

    #: the name of the index in ElasticSearch to be updated.
    index = luigi.Parameter()
    #: the name of the document type.
    doc_type = luigi.Parameter()
    #: the host running the ElasticSearch service.
    host = 'localhost'
    #: the port used by the ElasticSearch service.
    port = 9200
    
    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.SenpyTask`
        :return: object (:py:class:`luigi.task.Task`)
        """
        return SenpyTask(self.filename,self.analysis)

class SemanticTask(luigi.Task):
    """
    This task loads JSON data contained in a :py:class:`luigi.target.Target` and transform into RDF file
    to insert into Fuseki platform as a semantic 
    """
    #: date task parameter (default = today)
    date = luigi.DateParameter(default=datetime.date.today())
    file = str(random.randint(0,10000)) + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    def output(self):
        """
        Returns the target output for this task.
        In this case, a successful execution of this task will create a file on the local filesystem.
        :return: the target output for this task.
        :rtype: object (:py:class:`luigi.target.Target`)
        """
        return luigi.LocalTarget(path='/tmp/transformed-%s.n3' % self.file)


    def requires(self):
        """
        This task's dependencies:
        * :py:class:`~.SenpyTask` 
        :return: object (:py:class:`luigi.task.Task`)
        """
        return SenpyTask()

    def run(self):
        """
        Receive data from Senpy and transform them to RDF format in order to be indexed in Fuseki
        """
        with self.input().open('r') as infile:
            j = json.load(infile)
            g = Graph().parse(data=j, format='json-ld')
        with self.output().open('w') as output:
            output.write(g.serialize(format='n3', indent=4))
        
	
if __name__ == "__main__":
    #luigi.run(['--task', 'Elasticsearch'])
    luigi.run(	)