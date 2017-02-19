## Cannonade
Cannonade is a web API that allows for the benchmarking of web apps and services in a manner similiar to Apache Bench to be performed programtically and remotley, whilst saving the results in a central location so they can be fetched and maniuplated at a later time.

## Usage

Request to run a benchmark with 10 requests

```
curl -v -X "POST" http://localhost:5000/methods -d '{ "method": "run_benchmark", "url": "http://somedomain.com", "numbers": 10 }' -H 'Content-Type: application/json'
```

Response
```
{"meta": {"status": "200", "endpoint": "methods", "request_time": 1487535573}, "data": {"attributes": {"type": "Remote Method", "request": {"url": "http://somedomain.com", "numbers": 10}, "results": {"requests_process": 0.028953075408935547, "RPS": 345.38645234605315, "total": 10, "min": 0.0025539398193359375, "exec_time": 0.029664039611816406, "max": 0.0040400028228759766, "total_failed": 0, "total_success": 10, "time_per_request": 0.0028953075408935545}, "method": "run_benchmark"}}, "id": 44, "error": {}}
```
Request to fetch a past benchmark request
```
curl localhost:5000/benchmarks/44
```
Response
```
{"meta": {"status": "200", "endpoint": "fetchBenchmark", "request_time": 1487535725}, "data": {"attributes": {"id": "44", "request": {"url": "http://somedomain.com", "numbers": 10}, "type": "Remote Method", "results": {"requests_process": 0.028953075408935547, "RPS": 345.38645234605315, "total_success": 10, "min": 0.0025539398193359375, "exec_time": 0.029664039611816406, "max": 0.0040400028228759766, "total_failed": 0, "total": 10, "time_per_request": 0.0028953075408935545}, "method": "run_benchmark"}}, "error": {}}
```
