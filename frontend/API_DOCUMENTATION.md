# ExperLinx Backend API Documentation

This document describes the API endpoints available in the ExperLinx backend and how to use them from the frontend.

## Base URL
All API endpoints are prefixed with `/api/v1/`

## Authentication
Most endpoints require authentication using JWT tokens. After successful login, the backend returns an access token that should be included in the `Authorization` header for subsequent requests:

```
Authorization: Bearer <access_token>
```

## API Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "name": "string",
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer"
  }
}
```

#### POST /auth/login
Login with existing credentials.

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer"
  }
}
```

#### POST /auth/refresh
Refresh an expired access token using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer"
  }
}
```

### User Management

#### GET /users/me
Get the profile of the currently authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "name": "string",
    "email": "string",
    "role": "string",
    "created_at": "datetime"
  }
}
```

#### PATCH /users/me
Update the profile of the currently authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "string",
  "email": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "name": "string",
    "email": "string",
    "role": "string",
    "created_at": "datetime"
  }
}
```

#### GET /users/me/api-keys
List all API keys for the current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "string",
      "name": "string",
      "key_prefix": "string",
      "created_at": "datetime"
    }
  ]
}
```

#### POST /users/me/api-keys
Create a new API key for the current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "name": "string",
    "key": "string",  // Full key shown only once
    "created_at": "datetime"
  }
}
```

#### DELETE /users/me/api-keys/{key_id}
Revoke an API key for the current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": true
}
```

### Tools

#### GET /tools
List all available AI tools.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "endpoint_url": "string"
    }
  ]
}
```

#### GET /tools/{tool_id}
Get details for a specific tool.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "name": "string",
    "description": "string",
    "endpoint_url": "string"
  }
}
```

#### POST /tools/{tool_id}/invoke
Invoke a specific tool with input data.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "input": {}
}
```

**Response:**
```json
{
  "success": true,
  "data": {}
}
```

### Subscriptions

#### GET /subscriptions/plans
Get available subscription plans.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "price": "number",
      "features": ["string"]
    }
  ]
}
```

#### GET /subscriptions/current
Get the current user's subscription.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "plan_id": "string",
    "status": "string",
    "expires_at": "datetime"
  }
}
```

#### POST /subscriptions
Subscribe to a plan.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "plan_id": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "plan_id": "string",
    "status": "string",
    "expires_at": "datetime"
  }
}
```

### Usage

#### GET /usage/history
Get the user's usage history.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `start_date`: Filter from date (optional)
- `end_date`: Filter to date (optional)
- `page`: Page number (optional)
- `limit`: Items per page (optional)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "string",
      "tool_id": "string",
      "tool_name": "string",
      "tokens_used": "number",
      "timestamp": "datetime"
    }
  ]
}
```

#### GET /usage/summary
Get usage summary for the current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_tokens": "number",
    "period_start": "datetime",
    "period_end": "datetime"
  }
}
```

## Health Checks

#### GET /health
Health check endpoint for liveness probe.

**Response:**
```json
{
  "status": "ok"
}
```

#### GET /ready
Readiness check endpoint for readiness probe.

**Response:**
```json
{
  "status": "ready",
  "database": "connected"
}
```

## Error Handling

All API responses follow the same structure:

```json
{
  "success": true/false,
  "data": {} // or array of items
}
```

When success is false, the response includes an error:

```json
{
  "success": false,
  "error": "error message"
}
```

## Frontend Implementation Tips

1. Store the access token in localStorage or sessionStorage after login
2. Include the token in the Authorization header for all authenticated requests
3. Handle token expiration by refreshing the token when receiving a 401 response
4. Use the provided API service in `src/services/api.js` to make requests
5. Implement proper error handling for API responses