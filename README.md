# WriteShelf

A web-based digital bookshelf application built with Flask and MongoDB.

## Prerequisites

- Python 3.9+
- MongoDB
- Docker (for containerized deployment)
- Azure CLI (for Azure deployment)

## Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
MONGO_URI=your_mongodb_connection_string
SECRET_KEY=your_secret_key
```

4. Run the application:
```bash
flask run
```

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t writeshelf .
```

2. Run the container:
```bash
docker run -p 8000:8000 \
  -e MONGO_URI=your_mongodb_connection_string \
  -e SECRET_KEY=your_secret_key \
  writeshelf
```

## Azure Deployment

1. Login to Azure:
```bash
az login
```

2. Create Azure Container Registry (ACR):
```bash
az acr create --name writeshelf --resource-group your-resource-group --sku Basic --admin-enabled true
```

3. Build and push to ACR:
```bash
az acr build --registry writeshelf --image writeshelf .
```

4. Create App Service:
```bash
az webapp create --resource-group your-resource-group \
  --plan your-app-service-plan \
  --name your-app-name \
  --deployment-container-image-name writeshelf.azurecr.io/writeshelf:latest
```

5. Configure environment variables:
```bash
az webapp config appsettings set --resource-group your-resource-group \
  --name your-app-name \
  --settings MONGO_URI="your_mongodb_connection_string" SECRET_KEY="your_secret_key"
```

## Railway Deployment

1. Fork this repository to your GitHub account.

2. Create a new project on Railway.com and connect it to your GitHub repository.

3. Add the following environment variables in Railway:
   - `MONGO_URI`: Your MongoDB connection string
   - `SECRET_KEY`: A secure secret key for Flask sessions
   - `FLASK_ENV`: Set to 'production'
   - `PORT`: Set to 8000

4. Railway will automatically detect the Dockerfile and deploy your application.

5. Your application will be available at the URL provided by Railway.

## Environment Variables

- `MONGO_URI`: MongoDB connection string
- `SECRET_KEY`: Flask secret key for session management
- `FLASK_ENV`: Set to 'production' for deployment
- `WEBSITES_PORT`: Set to 8000 for Azure deployment

## Features

- User authentication and authorization
- Book upload and management
- PDF reader functionality
- User profiles and preferences
- Search functionality
- Review system

## Testing

Run tests with pytest:
```bash
pytest tests/
```

## Security Notes

- Never commit `.env` file or sensitive credentials
- Use Azure Key Vault for production secrets
- Keep dependencies updated
- Enable CORS only for trusted domains
- Use HTTPS in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License
