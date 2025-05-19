# Flask Server

A basic Flask server with CORS support and environment configuration.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5000
```

## Running the Server

1. Make sure your virtual environment is activated
2. Run the server:
```bash
python app.py
```

The server will start on http://localhost:5000

## Available Endpoints

- `GET /`: Welcome message
- `GET /api/health`: Health check endpoint

## Development

The server includes:
- CORS support for cross-origin requests
- Environment variable configuration
- Basic error handling
- Health check endpoint 