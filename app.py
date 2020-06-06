from flask import Flask
from apis import blueprint as api

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/v1')
app.run(debug=True)

# from flask import Flask
# from apis import api

# app = Flask(__name__)
# api.init_app(app)

# app.run(debug=True)
