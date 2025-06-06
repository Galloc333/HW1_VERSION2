import argparse
from website import create_app

app = create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run Flask server")
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    app.config['PORT'] = args.port
    app.run(debug=True, host='127.0.0.1', port=args.port)
