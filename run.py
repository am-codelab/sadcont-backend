from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render te da el PORT
    app.run(host="0.0.0.0", port=port, debug=True)

    # app.run(host="0.0.0.0", port=5000, debug=True)