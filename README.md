# StackSense

StackSense is a powerful tool designed to detect and identify SaaS (Software as a Service) products in your development environment. Built with a modern tech stack, it provides real-time insights into the software stack running in your workspace.

## 🚀 Features

- **Automatic SaaS Detection**: Identifies SaaS products and services in your development environment
- **Real-time Monitoring**: Continuously monitors your environment for software stack changes
- **Modern Tech Stack**: Built with FastAPI and Next.js for optimal performance and developer experience
- **RESTful API**: Clean, documented API for easy integration
- **Responsive UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS

## 🏗️ Architecture

StackSense follows a monorepo structure with separate frontend and backend applications:

```
stacksense/
├── apps/
│   ├── backend/          # FastAPI Python backend
│   └── frontend/         # Next.js frontend application
├── CODEOWNERS
└── LICENSE
```

### Backend

The backend is built with **FastAPI**, providing:
- Fast, modern Python web framework
- Automatic API documentation
- Type validation
- Async support

### Frontend

The frontend is built with **Next.js 16**, featuring:
- React 19
- TypeScript
- Tailwind CSS 4
- Server-side rendering
- API route support

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.8 or higher
- **Node.js** 18.x or higher
- **npm** or **yarn** package manager

## 🔧 Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd apps/backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn
```

4. Run the backend server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. API documentation will be available at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd apps/frontend/stacksense
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## 📖 Usage

### API Endpoints

Once the backend is running, you can interact with the API:

- **GET** `/`: Health check endpoint
- **GET** `/docs`: Interactive API documentation (Swagger UI)
- **GET** `/redoc`: Alternative API documentation

Example API call:
```bash
curl http://localhost:8000/
```

### Frontend

Access the web interface at `http://localhost:3000` to:
- View detected SaaS products
- Monitor your development environment
- Get insights about your software stack

## 🧪 Development

### Backend Development

The backend uses FastAPI's auto-reload feature for development. Make changes to `main.py` and see them reflected immediately.

### Frontend Development

The frontend uses Next.js hot module replacement. Changes to files in the `app` directory will automatically refresh in the browser.

### Linting

Run the frontend linter:
```bash
cd apps/frontend/stacksense
npm run lint
```

## 📝 Scripts

### Backend
- `uvicorn main:app --reload`: Start development server with auto-reload

### Frontend
- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run start`: Start production server
- `npm run lint`: Run ESLint

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please ensure your code follows the existing style and includes appropriate tests.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 👤 Maintainer

- akmukhi

## 🔮 Roadmap

Future enhancements include:
- Enhanced SaaS detection algorithms
- Integration with popular development tools
- Custom detection rules
- Export capabilities
- Historical tracking
- Dashboard analytics

---

Built with ❤️ using FastAPI and Next.js

