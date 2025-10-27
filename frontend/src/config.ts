import { OpenAPI } from './client/core/OpenAPI';

// Configure the API base URL
// The generated client paths are relative to /api/v1 (from the OpenAPI schema)
// So we need to include /api/v1 in the base URL
const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
OpenAPI.BASE = `${baseUrl}/api/v1`;

export default OpenAPI;
