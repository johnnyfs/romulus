#!/bin/bash

# Script to generate TypeScript client from FastAPI OpenAPI schema
# Usage: ./generate-client.sh

source .env

set -e

# Configuration
API_URL="http://localhost:${BACKEND_PORT:-8000}"
OPENAPI_FILE="openapi.json"
OUTPUT_DIR="./frontend/src/client"

echo "🚀 Generating TypeScript client from FastAPI OpenAPI schema..."

# Step 1: Fetch the OpenAPI schema
echo "📥 Fetching OpenAPI schema from ${API_URL}/api/v1/openapi.json..."
curl -s "${API_URL}/api/v1/openapi.json" -o "${OPENAPI_FILE}"

if [ ! -f "${OPENAPI_FILE}" ]; then
    echo "❌ Failed to fetch OpenAPI schema. Make sure FastAPI is running at ${API_URL}"
    exit 1
fi

echo "✅ OpenAPI schema downloaded"

# Step 2: Generate TypeScript client using openapi-typescript-codegen
echo "🔧 Generating TypeScript client..."
cd frontend && npx openapi-typescript-codegen \
    --input "../${OPENAPI_FILE}" \
    --output "src/client" \
    --client fetch
cd ..

# Clean up
echo "🧹 Cleaning up..."
rm "${OPENAPI_FILE}"

echo "✨ TypeScript client generated successfully at ${OUTPUT_DIR}"
echo ""
echo "📝 Next steps:"
echo "   1. Review the generated client in ${OUTPUT_DIR}"
echo "   2. Import and use the client in your React components"
echo "   3. Example usage:"
echo "      import { DefaultService } from './client';"
echo "      const data = await DefaultService.getSomething();"
