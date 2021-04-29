from werkzeug.middleware.profiler import ProfilerMiddleware
from studio import create_app
app = create_app()
app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app,restrictions=[30])
app.run(debug=True)