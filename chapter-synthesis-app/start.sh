#!/bin/bash

echo "=========================================="
echo "  Chapter Synthesis Platform"
echo "  Advanced Medical Knowledge Synthesis"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env file from template..."
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env (please review and update if needed)"
fi

# Start services
echo ""
echo "🚀 Starting services..."
echo ""
docker-compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "=========================================="
echo "  ✅ Application Started Successfully!"
echo "=========================================="
echo ""
echo "🌐 Access Points:"
echo "   Frontend:       http://localhost:3000"
echo "   Backend API:    http://localhost:8000"
echo "   API Docs:       http://localhost:8000/docs"
echo ""
echo "📝 Next Steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Click 'Register here' to create an account"
echo "   3. Login and explore the dashboard"
echo ""
echo "🛠️  Useful Commands:"
echo "   View logs:      docker-compose logs -f"
echo "   Stop services:  docker-compose down"
echo "   Restart:        docker-compose restart"
echo ""
echo "📖 For more information, see README.md"
echo ""
