from flask import Flask, request, g, Response
import surcharge.core as surcharge
import json
import time
import sqlite3
import inspect

DATABASE = 'benchmarks'

app = Flask(__name__)

# SQLite get_db function
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Builds a Basic Response dictionary  
def buildResponse(attributes, errors, status):
  currentTime = int(time.time())
  responseDict = {}
  curframe = inspect.currentframe()
  calframe = inspect.getouterframes(curframe, 2)
  responseDict['meta'] = { 'status': status, 'request_time': currentTime, 'endpoint': calframe[1][3] }
  responseDict['data'] = { 'attributes': attributes }
  responseDict['error'] = errors
  return responseDict

# Process for closing connection to sqlite on shutdown
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Endpoint for accessing the methods endpoint
@app.route('/methods', methods = ['POST', 'GET'])
def methods():
  conn = get_db()
  cur = conn.cursor()
  if request.method == 'POST':
    if 'method' in request.json:
      method = request.json['method']  
      if method == 'run_benchmark':       
        try:
           argsJson = request.json
           argsJson.pop('method', None)
           surcharger_args = argsJson
        except:
          error = { "message:": "You must pass arguments to the benchmark endpoint as a json document" }
          response = buildResponse({}, error, '400')
          return Response(json.dumps(response), mimetype='application/json'), 400

        try: 
          surcharger = surcharge.Surcharger(**surcharger_args)
        except Exception as e:
          print sys.exc_info()[0].message.__str__
          error = { "message:": "Could not process benchmark with arguments provided", "exception": e }
          response = buildResponse({}, error, '500')
          return Response(json.dumps(response), mimetype='application/json'), 500

        try:
          surcharger()
        except Exception as e:
          error = { "message:": e}
          response = buildResponse({}, error, '500')
          return Response(json.dumps(response), mimetype='application/json'), 500
        
        stats = surcharge.SurchargerStats(surcharger=surcharger)
        stats()
        attributes = { "request": surcharger_args, "results": stats.stats, "type": "Remote Method", "method": method }
        response = buildResponse(attributes, {}, '200')
        insertString = "insert into benchmarks (result) values ('{0}')".format(json.dumps(attributes))
        cur.execute(insertString)
        conn.commit()
        response['id'] = cur.lastrowid
        return Response(json.dumps(response), mimetype='application/json')
      else:
        error = { "message:": "unknown method"}
        response = buildResponse({}, error, '400')
        return Response(json.dumps(response), mimetype='application/json'), 400
    else:
      error = { "message:": "You must provide a valid method to the methods endpoint"}
      response = buildResponse({}, error, '400')
      return Response(json.dumps(response), mimetype='application/json'), 400
       
  else:
    return Response('{"message": "nothing to see here"}', mimetype='application/json'), 405
     
# Endpoint to fetch past benchmarks
@app.route('/benchmarks/<id>')
def fetchBenchmark(id):
  if request.method == 'GET':
    conn = get_db()
    cur = conn.cursor()
    query = "select result from benchmarks where id = {0}".format(id)
    cur.execute(query)
    try: 
      attributes = json.loads(cur.fetchone()[0])
      attributes['id'] = id 
      response = buildResponse(attributes, {}, '200')    
      return Response(json.dumps(response), mimetype='application/json')
    except:
      return Response('{ "message": "ID not found"}', mimetype='application/json'), 404
    
  else:
    return Response('{"message": "nothing to see here"}', mimetype='application/json'),405

if __name__ == '__main__':
    app.run(threaded=True, host="0.0.0.0")
