import argparse
from studio import create_app
from datetime import timedelta

parser = argparse.ArgumentParser()
parser.add_argument("--port", help="Port for debug server to listen on", default=5000)
args = parser.parse_args()
app = create_app()

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=5)
app.run(debug=True, host='127.0.0.1', port=args.port)
