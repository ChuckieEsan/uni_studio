import argparse
from studio import create_app
parser = argparse.ArgumentParser()
parser.add_argument("--port",help="Port for debug server to listen on",default=5000)
args = parser.parse_args()
app = create_app()

app.run(debug=True,host='127.0.0.1',port=args.port)