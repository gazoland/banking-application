from flask import Flask

from src.api import api_bp


app = Flask(__name__)
app.config["SECRET_KEY"] = 'thisismysecretkey'  # os.environ.get("BANKING_SYSTEM_APP_KEY")
app.register_blueprint(api_bp)

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)  # Switch to False
