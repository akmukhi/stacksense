# StackSense Backend

The backend for StackSense - a SaaS product detection system.

## 🛠️ Technology

- **FastAPI**: Modern, fast web framework for building APIs with Python

## 📋 Prerequisites

- Python 3.8 or higher

## 🔧 Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install fastapi uvicorn
```

## 🚀 Running

Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at:
- **API**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📖 Current Endpoints

- **GET** `/`: Returns a simple "Hello World!" message

## 📝 Development

The server runs with auto-reload enabled, so changes to `main.py` will be reflected immediately.

