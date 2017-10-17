from flask import Flask, abort, render_template, json
from flask_cache import Cache
from OsirisAPI import OsirisAPI

app = Flask(__name__)
cache = Cache(app,config={
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'fcache',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': '6379',
    'CACHE_REDIS_URL': 'redis://localhost:6379'
})

@app.route('/api/types/')
def types():
    return json.dumps(OsirisAPI.Types)

@app.route('/api/faculties/')
def faculties():
    return json.dumps(OsirisAPI.Faculties)

@app.route('/api/course/<code>/')
@cache.cached(timeout=24*60*60)
def coursecode(code):
    API = OsirisAPI()
    info = API.getCourseInfo(code)
    if info is None:
        abort(404)
    return json.dumps(info)

@app.route('/api/faculty/courses/<faculty>/level/<int:level>/')
@cache.cached(timeout=24*60*60)
def facultcourseslevel(faculty, level):
    API = OsirisAPI()
    level = int(level)
    if faculty not in [f[0] for f in API.Faculties] or level > 3 or level < 0:
        abort(404)
    info = API.getCoursesLevel(faculty, level)
    if info is None:
        abort(404)
    return json.dumps(info)

@app.route('/api/faculty/courses/<faculty>/<type>/')
@cache.cached(timeout=24*60*60)
def facultycoursestype(faculty, type):
    API = OsirisAPI()
    if faculty not in [f[0] for f in API.Faculties] or type not in [t[0] for t in API.Types]:
        abort(404)
    info = API.getCourses(faculty, type)
    if info is None:
        abort(404)
    return json.dumps(info)

@app.route('/')
def index():
    return render_template('index.html', name='index')

if __name__ == '__main__':
    app.run()
