# ExperLinx Frontend

This is the frontend application for the ExperLinx platform, designed to connect to the backend API.

## Setup

1. Make sure the backend is running on `http://localhost:8000`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```
4. The frontend will be available at `http://localhost:3000`

## Environment Variables

Create a `.env` file in the root of the frontend directory:

```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## API Integration

The frontend uses the API service in `src/services/api.js` to communicate with the backend. This service handles:

- Authentication (login, registration, token refresh)
- User management (profile, API keys)
- Tool access (listing, invocation)
- Subscription management
- Usage tracking

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm run build` - Builds the app for production
- `npm test` - Runs tests
- `npm run eject` - Ejects from Create React App (irreversible)

## API Documentation

For detailed information about the backend API endpoints, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).