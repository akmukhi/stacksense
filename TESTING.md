# Testing Instructions

This document provides comprehensive testing instructions for the StackSense FastAPI backend and Next.js frontend.

## Prerequisites

Before testing, ensure you have:

- **Python 3.8+** installed
- **Node.js 18.x+** installed
- **npm** or **yarn** package manager
- Both backend and frontend dependencies installed

## Backend Testing

### Setup

1. Navigate to the backend directory:
```bash
cd apps/backend
```

2. Activate the virtual environment (if using one):
```bash
source env/bin/activate  # On macOS/Linux
# or
env\Scripts\activate  # On Windows
```

3. Install dependencies (if not already installed):
```bash
pip install -r requirements.txt
```

4. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The server should start on `http://localhost:8000`

### Testing Endpoints

#### 1. Root Endpoint (`GET /`)

**Using curl:**
```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "message": "Hello World from FastAPI!"
}
```

**Using browser:**
Navigate to: `http://localhost:8000/`

**Using Python requests:**
```python
import requests
response = requests.get("http://localhost:8000/")
print(response.json())
```

#### 2. Hello Endpoint (`GET /api/hello`)

**Using curl:**
```bash
curl http://localhost:8000/api/hello
```

**Expected Response:**
```json
{
  "message": "Hello World!",
  "status": "success",
  "framework": "FastAPI"
}
```

**Using browser:**
Navigate to: `http://localhost:8000/api/hello`

**Using Python requests:**
```python
import requests
response = requests.get("http://localhost:8000/api/hello")
print(response.json())
```

#### 3. API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

You can test endpoints directly from these pages.

### Testing CORS

To verify CORS is working correctly:

1. Start the backend server
2. Start the frontend server (see Frontend Testing below)
3. Open browser DevTools (F12)
4. Check the Network tab - requests from `http://localhost:3000` to `http://localhost:8000` should succeed without CORS errors

**Using curl to test CORS headers:**
```bash
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8000/api/hello -v
```

You should see CORS headers in the response.

## Frontend Testing

### Setup

1. Navigate to the frontend directory:
```bash
cd apps/frontend/stacksense
```

2. Install dependencies (if not already installed):
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend should start on `http://localhost:3000`

### Manual Testing

1. **Open the application:**
   - Navigate to `http://localhost:3000` in your browser

2. **Test successful connection:**
   - Ensure the backend is running on `http://localhost:8000`
   - The page should display:
     - "Hello World!" message from the backend
     - Framework: FastAPI
     - Status: success

3. **Test error handling:**
   - Stop the backend server
   - Refresh the frontend page
   - You should see an error message indicating the backend is not available
   - The error should include instructions to start the FastAPI server

4. **Test loading state:**
   - Open browser DevTools (F12)
   - Go to Network tab
   - Throttle network to "Slow 3G"
   - Refresh the page
   - You should briefly see "Loading..." before the data appears

### Browser DevTools Testing

1. **Open DevTools** (F12 or Cmd+Option+I on Mac)

2. **Console Tab:**
   - Check for any JavaScript errors
   - Verify no CORS errors
   - Check for network errors

3. **Network Tab:**
   - Filter by "Fetch/XHR"
   - Refresh the page
   - Verify the request to `http://localhost:8000/api/hello`
   - Check response status (should be 200)
   - Verify response payload matches expected format

4. **Application Tab:**
   - Check for any storage issues
   - Verify no service worker conflicts

## Integration Testing

### End-to-End Test Flow

1. **Start Backend:**
   ```bash
   cd apps/backend
   uvicorn main:app --reload
   ```

2. **Start Frontend:**
   ```bash
   cd apps/frontend/stacksense
   npm run dev
   ```

3. **Test Flow:**
   - Open `http://localhost:3000`
   - Verify the page loads without errors
   - Verify the backend message is displayed
   - Verify the tech stack information is shown
   - Check browser console for errors
   - Verify network requests are successful

### Testing Different Scenarios

#### Scenario 1: Both servers running
- **Expected:** Frontend displays backend message successfully
- **Status:** ✅ Should work

#### Scenario 2: Backend stopped
- **Expected:** Frontend shows error message
- **Status:** ✅ Should show error handling

#### Scenario 3: Backend on different port
- **Expected:** Frontend shows connection error
- **Status:** ✅ Should show error handling

#### Scenario 4: Backend slow response
- **Expected:** Frontend shows loading state, then data
- **Status:** ✅ Should handle gracefully

## Automated Testing (Future)

### Backend Unit Tests

Create `apps/backend/test_main.py`:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World from FastAPI!"}

def test_hello():
    response = client.get("/api/hello")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello World!"
    assert data["status"] == "success"
    assert data["framework"] == "FastAPI"
```

Run tests:
```bash
pytest test_main.py
```

### Frontend Component Tests

Create `apps/frontend/stacksense/__tests__/page.test.tsx`:

```typescript
import { render, screen, waitFor } from '@testing-library/react'
import Home from '../app/page'

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({
      message: "Hello World!",
      status: "success",
      framework: "FastAPI"
    }),
  })
) as jest.Mock

describe('Home Page', () => {
  it('renders the page', async () => {
    render(<Home />)
    await waitFor(() => {
      expect(screen.getByText(/Hello World!/i)).toBeInTheDocument()
    })
  })
})
```

## Troubleshooting

### Common Issues

1. **CORS Errors:**
   - Verify backend CORS middleware is configured
   - Check that `allow_origins` includes `http://localhost:3000`
   - Verify backend is running

2. **Connection Refused:**
   - Ensure backend server is running on port 8000
   - Check for port conflicts
   - Verify firewall settings

3. **Module Not Found:**
   - Reinstall dependencies: `pip install -r requirements.txt` (backend)
   - Reinstall dependencies: `npm install` (frontend)

4. **TypeScript Errors:**
   - Run `npm run build` to check for type errors
   - Verify all types are properly defined

5. **Port Already in Use:**
   - Backend: Change port with `uvicorn main:app --reload --port 8001`
   - Frontend: Change port with `npm run dev -- -p 3001`
   - Update frontend API URL accordingly

## Performance Testing

### Backend Performance

Test response times:
```bash
# Using curl with timing
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/hello

# Create curl-format.txt:
# time_namelookup:  %{time_namelookup}\n
# time_connect:  %{time_connect}\n
# time_starttransfer:  %{time_starttransfer}\n
# time_total:  %{time_total}\n
```

### Frontend Performance

1. Open Chrome DevTools
2. Go to Lighthouse tab
3. Run performance audit
4. Check for:
   - First Contentful Paint
   - Time to Interactive
   - Total Blocking Time

## Security Testing

1. **CORS Configuration:**
   - Verify only allowed origins can access the API
   - Test with different origin headers

2. **Input Validation:**
   - Test endpoints with invalid data
   - Verify proper error responses

3. **Headers:**
   - Check security headers in responses
   - Verify no sensitive information in headers

## Test Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Root endpoint (`/`) returns correct response
- [ ] Hello endpoint (`/api/hello`) returns correct response
- [ ] Frontend displays backend message
- [ ] Error handling works when backend is down
- [ ] Loading state displays correctly
- [ ] CORS is properly configured
- [ ] No console errors in browser
- [ ] API documentation is accessible
- [ ] Network requests are successful
- [ ] Page is responsive on different screen sizes

## Additional Resources

- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Next.js Testing](https://nextjs.org/docs/app/building-your-application/testing)
- [API Documentation](http://localhost:8000/docs) (when backend is running)

