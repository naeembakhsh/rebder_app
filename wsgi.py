from app import app  # Make sure this matches your Flask app variable name

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)  # Render requires these settings
