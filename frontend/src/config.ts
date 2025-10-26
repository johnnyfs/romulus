import { OpenAPI } from './client/core/OpenAPI';

// Configure the API base URL
OpenAPI.BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default OpenAPI;
