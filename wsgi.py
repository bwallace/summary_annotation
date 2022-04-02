#from gevent.pywsgi import WSGIServer
from app_struct_sum import app
#http_server = WSGIServer(('', 5000), app)
#http_server.serve_forever()
if __name__ == "__main__":
    app.run()
