from app import create_app

app = create_app()

if __name__ == '__main__':
    # To run the app:
    # 1. Set the Flask app environment variable:
    #    On Windows: set FLASK_APP=run.py
    #    On macOS/Linux: export FLASK_APP=run.py
    # 2. Run the flask command:
    #    flask run
    app.run(debug=True)
