from flask import Flask, request, g, Response
import surcharge.core as surcharge
import json
import time
import sqlite3

DATABASE = 'benchmarks'

app = Flask(__name__)

# SQLite get_db function
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Builds a Basic Response dictionary  
def buildResponse(attributes,errors):
  currentTime = int(time.time())
  responseDict = {}
  responseDict['meta'] = { 'request_time': currentTime }
  responseDict['data'] = { 'attributes': attributes }
  responseDict['error'] = errors
  return responseDict

# Process for closing connection to sqlite on shutdown
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Endpoint for accessing the benchmark method
@app.route('/run_benchmark', methods = ['POST', 'GET'])
def benchmark():
  conn = get_db()
  cur = conn.cursor()
  if request.method == 'POST':

    try:
       surcharger_args = request.json
    except:
      error = { "message:": "You must pass arguments to the benchmark endpoint as a json document" }
      response = buildResponse({}, error)
      return Response(json.dumps(response), mimetype='application/json')

    try: 
      surcharger = surcharge.Surcharger(**surcharger_args)
    except:
      error = { "message:": "Could not process benchmark with arguments provided" }
      response = buildResponse({}, error)
      return Response(json.dumps(response), mimetype='application/json')

    try:
      surcharger()
    except error as e:
      error = { "message:": e}
      response = buildResponse({}, error)
      return Response(json.dumps(response), mimetype='application/json')
    
    stats = surcharge.SurchargerStats(surcharger=surcharger)
    stats()
    attributes = { "request": surcharger_args, "results": stats.stats, "type": "URL Benchmark Test" }
    response = buildResponse(attributes, {})
    insertString = "insert into benchmarks (result) values ('{0}')".format(json.dumps(response))
    cur.execute(insertString)
    conn.commit()
    response['id'] = cur.lastrowid
    return Response(json.dumps(response), mimetype='application/json')
  else:
    return Response('{"message": "nothing to see here"}', mimetype='application/json')
     
# Endpoint to fetch past benchmarks
@app.route('/benchmarks/<id>')
def fetchBenchmark(id):
  if request.method == 'GET':
    conn = get_db()
    cur = conn.cursor()
    query = "select result from benchmarks where id = {0}".format(id)
    cur.execute(query)
    try: 
      response = json.loads(cur.fetchone()[0])
      response['id'] = id     
      return Response(json.dumps(response), mimetype='application/json')
    except:
      return Response('{ "message": "ID not found"}', mimetype='application/json')
    
  else:
    return Response('{"message": "nothing to see here"}', mimetype='application/json')

if __name__ == '__main__':
    app.run(threaded=True, host="0.0.0.0")
