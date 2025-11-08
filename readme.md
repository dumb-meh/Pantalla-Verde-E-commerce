# Pantalla-Verde-E-commerce AI Service

An AI-powered e-commerce assistant service that provides intelligent product suggestions and conversational support with real-time inventory tracking.

## 🚀 Features

- **AI Product Suggestions**: Generate compelling product descriptions, competitive pricing, and relevant tags
- **Intelligent Chatbot**: Multi-lingual conversational AI with vector search capabilities
- **Real-time Stock Tracking**: Live inventory status integration with external product API
- **Vector Database Search**: ChromaDB-powered semantic search for product information
- **Conversation Memory**: Maintains context across chat interactions
- **RESTful API**: Well-structured API endpoints for all services

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- OpenAI API Key
- Access to product API endpoint

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI
- **AI/ML**: OpenAI GPT-4o-mini
- **Vector Database**: ChromaDB
- **Web Server**: Nginx (reverse proxy)
- **Containerization**: Docker
- **Async Operations**: aiohttp

## 📦 Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd adrianabrill-ai-service
```

2. Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The service will be available at `http://localhost:8086`

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file as shown above

4. Run the application:
```bash
python main.py
```

The service will be available at `http://localhost:8085`

## 🔌 API Endpoints

### Base URL
- Docker: `http://localhost:8086`
- Local: `http://localhost:8085`

### Available Endpoints

#### 1. Health Check
```http
GET /health
```
Returns service health status

#### 2. AI Product Suggestions
```http
POST /api/ai_suggestions
```
**Request Body:**
```json
{
  "product_name": "string",
  "brand": "string",
  "model": "string"
}
```
**Response:**
```json
{
  "description": "string",
  "price": "string",
  "tag": "string"
}
```

#### 3. Chat
```http
POST /api/chat
```
**Request Body:**
```json
{
  "message": "string",
  "history": [
    {
      "role": "user|assistant",
      "content": "string"
    }
  ]
}
```
**Response:**
```json
{
  "response": "string",
  "user_message": "string"
}
```

#### 4. Knowledge Management

**Add Product:**
```http
POST /api/knowledge/products
```
**Request Body:**
```json
{
  "productName": "string",
  "model": "string",
  "brand": "string",
  "type": "string",
  "color": "string",
  "status": "available|out_of_stock|discontinued",
  "price": 0.0,
  "priceWithInstallation": 0.0,
  "condition": "new|refurbished|used",
  "warrantyType": "manufacturer|extended|none",
  "description": "string"
}
```

**Search Products:**
```http
GET /api/knowledge/products/search?query=string&limit=5
```

**Get All Products:**
```http
GET /api/knowledge/products?limit=100
```

**Update Product:**
```http
PUT /api/knowledge/products/{product_id}
```

**Delete Product:**
```http
DELETE /api/knowledge/products/{product_id}
```

### API Documentation
Interactive API documentation available at:
- Swagger UI: `http://localhost:8086/docs`
- ReDoc: `http://localhost:8086/redoc`

## 🏗️ Project Structure

```
adrianabrill-ai-service/
├── app/
│   ├── core/
│   │   └── config.py           # Application configuration
│   ├── services/
│   │   ├── ai_suggestions/     # AI product suggestions service
│   │   │   ├── ai_suggestions.py
│   │   │   ├── ai_suggestions_route.py
│   │   │   └── ai_suggestions_schema.py
│   │   └── chat/               # Chatbot service
│   │      ├── chatbot.py
│   │      ├── chatbot_route.py
│   │      └── chatbot_schema.py
│   │   
│   │       
│   ├── utils/knowledge/         # Knowledge base operations
│   │        ├── knowledge.py
│   │        ├── knowledge_route.py
│   │        └── knowledge_schema.py      
│   └── vectordb/
│       └── config.py           # ChromaDB configuration
├── nginx/
│   └── nginx.conf              # Nginx configuration
├── chroma_db/                  # ChromaDB persistent storage
├── docker-compose.yml
├── Dockerfile
├── main.py                     # FastAPI application entry
├── requirements.txt
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | Yes |

### External Dependencies

The chatbot service integrates with an external product API:
- Base URL: `https://fzjn9pz1-5101.inc1.devtunnels.ms/api/v1/products`
- Used for real-time stock information

## 🚦 How It Works

### AI Suggestions Flow
1. Receives product details (name, brand, model)
2. Uses GPT-4o-mini to generate descriptions, pricing, and tags
3. Returns formatted suggestions without external references

### Chatbot Flow
1. Receives user message with optional conversation history
2. Analyzes intent and translates if necessary
3. Searches ChromaDB for relevant products
4. Fetches real-time stock for found products (concurrent API calls)
5. Generates contextual response using GPT-4o-mini
6. Returns response with user's original message

### Knowledge Management
1. Products are stored in ChromaDB with semantic embeddings
2. Supports CRUD operations for product management
3. Vector similarity search for intelligent product matching

## 🐳 Docker Configuration

### Services
- **app**: Main FastAPI application (port 8085 internal)
- **nginx**: Reverse proxy server (port 8086 external)

### Networks
- `adrianabrill_AI_network`: Bridge network for service communication

### Volumes
- `./chroma_db`: Persistent storage for vector database

## 📊 Performance Considerations

- Concurrent API calls for stock checking (up to 5 products simultaneously)
- Request timeout: 5 seconds per product API call
- ChromaDB uses cosine similarity for efficient vector search
- Nginx configured with gzip compression and appropriate timeouts

## 🔒 Security

- CORS configured (customize origins in production)
- Security headers implemented in Nginx
- API key management through environment variables
- No external references or URLs in AI responses

## 🧪 Testing

### Manual Testing with cURL

**Test AI Suggestions:**
```bash
curl -X POST http://localhost:8086/api/ai_suggestions \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Laptop",
    "brand": "Dell",
    "model": "XPS 13"
  }'
```

**Test Chat:**
```bash
curl -X POST http://localhost:8086/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Do you have any laptops in stock?",
    "history": []
  }'
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Change ports in `docker-compose.yml` and `nginx.conf`

2. **OpenAI API Errors**
   - Verify API key in `.env` file
   - Check API rate limits

3. **ChromaDB Issues**
   - Ensure `chroma_db` directory has proper permissions
   - Try resetting the collection through the API

4. **Docker Build Failures**
   - Clear Docker cache: `docker-compose build --no-cache`
   - Check Docker daemon status


---

**Note**: This service is designed for e-commerce applications and requires proper API keys and external service access for full functionality.