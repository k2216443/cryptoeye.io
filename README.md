# ChainEye 🔐

**Blockchain Wallet Security & Insights Platform**

ChainEye is a comprehensive security analysis platform for blockchain wallet addresses, providing real-time risk assessment and detailed insights for Ethereum (ERC20) and Tron (TRC20) networks.

![Version](https://img.shields.io/badge/version-v2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green)

---

## 🌟 Features

### Core Capabilities
- **Multi-Chain Support**: Analyze both Ethereum (ERC20) and Tron (TRC20) wallet addresses
- **Real-Time Analysis**: Instant security scoring and risk assessment
- **Rule-Based Engine**: Configurable security rules for comprehensive evaluation
- **Interactive Dashboard**: Modern, responsive web interface with animated visualizations
- **API Integration**: RESTful API for programmatic access
- **Telegram Bot**: Direct wallet analysis through Telegram

### Security Analysis
- Transaction history evaluation
- Smart contract interaction analysis
- Risk score calculation (0-100)
- Security flags and warnings
- Wallet age and activity metrics
- Balance and holdings information

### Infrastructure
- Containerized microservices architecture
- Automated CI/CD pipeline
- Multi-environment deployment
- JSON-formatted structured logging
- Real-time Telegram notifications

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Load Balancer (ALB)                  │
└───────────────────────┬─────────────────────────────────┘
                        │
           ┌────────────┴────────────┐
           │                         │
    ┌──────▼──────┐          ┌──────▼──────┐
    │   Static    │          │   API       │
    │   Site      │          │   Backend   │
    │  (Nginx)    │◄─────────│  (FastAPI)  │
    └─────────────┘          └──────┬──────┘
         │                          │
         │                   ┌──────▼──────────┐
         │                   │  Blockchain     │
         │                   │  Providers      │
         └───────────────────┤  - Etherscan    │
                            │  - TronScan     │
                            └─────────────────┘
```

### Components

#### Frontend
- **Framework**: Pure HTML/CSS/JavaScript
- **Design**: Glassmorphism with dark theme
- **Server**: Nginx (Alpine-based)
- **Port**: 80 (internal), proxied via ALB

#### Backend API
- **Framework**: FastAPI (Python 3.11+)
- **Port**: 8080
- **Features**: Async processing, structured logging, health checks

#### Scoring Engines
- **Ethereum Scorer** (`scorer_etherscan/`): ERC20 wallet analysis
- **Tron Scorer** (`scorer_tron/`): TRC20 wallet analysis

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- AWS CLI (for deployment)
- Etherscan API Key

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/k2216443/chaineye.io.git
cd chaineye.io
```

2. **Set up Python environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r src/api/requirements.txt
```

3. **Configure environment variables**
```bash
cd src/api
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the API locally**
```bash
cd src/api
python main.py
```

The API will be available at `http://localhost:8080`

5. **Run the static site** (optional)
```bash
cd src/static
docker build -t chaineye-site .
docker run -p 80:80 chaineye-site
```

Visit `http://localhost` to access the web interface.

---

## 🧪 Testing

### API Endpoints

**Health Check**
```bash
curl http://localhost:8080/health
```

**Evaluate Ethereum Address**
```bash
curl "http://localhost:8080/evaluate?addr=0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f91"
```

**Test Scripts**
```bash
# Ethereum
python src/api/test_eth.py

# Tron
python src/api/test_trc.py
```

---

## 📦 Docker Deployment

### Build Images

**API Container**
```bash
cd src/api
docker build -t chaineye-api:latest .
docker run -p 8080:8080 -e ETHERSCAN_API_KEY=your_key chaineye-api:latest
```

**Static Site Container**
```bash
cd src/static
docker build -t chaineye-site:latest .
docker run -p 80:80 chaineye-site:latest
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: ./src/api
    ports:
      - "8080:8080"
    environment:
      - ETHERSCAN_API_KEY=${ETHERSCAN_API_KEY}
      - BOT_TOKEN=${BOT_TOKEN}

  site:
    build: ./src/static
    ports:
      - "80:80"
    depends_on:
      - api
```

---

## 🏭 Production Deployment

### AWS Infrastructure

The project uses Terraform for infrastructure provisioning:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**Infrastructure Components:**
- **ECR**: Container registries for API and static site images
- **CodeBuild**: CI/CD pipeline with automated builds
- **ALB**: Application Load Balancer with SSL termination
- **Route53**: DNS management for chaineye.io
- **S3**: Terraform state backend

### CI/CD Pipeline

Automated deployment triggers on git push:

1. **Build Phase**: Build both API and static site Docker images
2. **Test Phase**: Run unit and integration tests
3. **Push Phase**: Push images to ECR with git-based versioning
4. **Notify Phase**: Send deployment status to Telegram

**Build Status Notifications:**
```
🚀 ChainEye Deployment

✅ Build and deployment successful!

Version: v2.0-abc1234
Commit: Add new feature
Author: Developer Name

Images:
• API: cryptoeye:v2.0-abc1234 ✅
• Static Site: chaineye-site:v2.0-abc1234 ✅
```

---

## 📚 API Documentation

### Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "ok": true
}
```

#### `GET /evaluate`
Evaluate wallet security.

**Parameters:**
- `addr` (required): Wallet address (0x... for ETH, T... for TRC)
- `chain` (optional): `ethereum` or `tron` (default: auto-detect)

**Response:**
```json
{
  "ok": true,
  "address": "0x...",
  "result": {
    "risk_score": 15,
    "risk_level": "low",
    "tx_count": 1250,
    "first_tx_date": "2020-03-15",
    "last_tx_date": "2025-10-17",
    "balance": "2.5 ETH",
    "flags": [
      {
        "severity": "info",
        "title": "Active Wallet",
        "description": "Recent transaction activity detected"
      }
    ]
  }
}
```

---

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **Python 3.11+**: Core language
- **Anyio**: Async I/O library
- **Pydantic**: Data validation
- **Python-JSON-Logger**: Structured logging

### Frontend
- **HTML5/CSS3/JavaScript**: Pure vanilla implementation
- **Nginx**: High-performance web server
- **JSON**: Structured log format

### Blockchain Integration
- **Etherscan API**: Ethereum blockchain data
- **TronScan API**: Tron blockchain data

### Infrastructure
- **Docker**: Containerization
- **Terraform**: Infrastructure as Code
- **AWS**: Cloud platform (ECR, CodeBuild, ALB, Route53)
- **Ansible**: Configuration management

### DevOps
- **AWS CodeBuild**: CI/CD pipeline
- **GitHub**: Version control
- **Telegram Bot API**: Deployment notifications

---

## 📁 Project Structure

```
chaineye.io/
├── src/
│   ├── api/                    # Backend API
│   │   ├── main.py            # FastAPI application
│   │   ├── providers/         # Blockchain API clients
│   │   ├── scorer_etherscan/  # Ethereum scoring engine
│   │   ├── scorer_tron/       # Tron scoring engine
│   │   ├── libs/              # Utility libraries
│   │   ├── Dockerfile         # API container image
│   │   └── requirements.txt   # Python dependencies
│   │
│   └── static/                # Frontend
│       ├── index.html         # Landing page
│       ├── evaluate.html      # Results page
│       ├── nginx.conf         # Web server config
│       └── Dockerfile         # Static site container
│
├── terraform/                 # Infrastructure as Code
│   ├── modules/               # Reusable Terraform modules
│   │   ├── codebuild/        # CI/CD configuration
│   │   └── lb/               # Load balancer setup
│   ├── bucket/               # S3 backend config
│   └── *.tf                  # Main Terraform files
│
├── ansible/                   # Configuration management
│   └── inventory/            # Environment configs
│
├── buildspec.yaml            # CodeBuild pipeline
├── CHANGELOG.md              # Version history
├── version                   # Current version
└── README.md                 # This file
```

---

## 🔧 Configuration

### Environment Variables

**API Configuration** (`src/api/.env`):
```bash
ETHERSCAN_API_KEY=your_etherscan_key
BOT_TOKEN=your_telegram_bot_token
LOG_LEVEL=INFO
LOG_FILE=/var/log/cryptoeye.json.log
```

**Terraform Variables** (`terraform/terraform.tfvars`):
```hcl
github_token = "your_github_token"
telegram_bot_token = "your_telegram_token"
ETHERSCAN_API_KEY = "your_etherscan_key"
```

---

## 🎨 UI Features

### Landing Page
- Real-time wallet address validation
- Network detection (Ethereum/Tron)
- Interactive example addresses
- Instant audit button
- Dark theme with cyan accents

### Security Report Page
- Animated risk score visualization
- Color-coded risk levels
- Security indicators
- Transaction history
- Wallet metrics

---

## 📊 Monitoring & Logging

### Structured Logging
All logs are output in JSON format for easy parsing:

```json
{
  "asctime": "2025-10-17T12:00:00Z",
  "level": "INFO",
  "name": "cryptoeye",
  "message": "Wallet evaluated",
  "event": "wallet_evaluation",
  "address": "0x...",
  "risk_score": 15,
  "request_id": "uuid"
}
```

### Deployment Notifications
Telegram notifications for all builds with:
- Build status (success/failure)
- Version and commit information
- Author and commit message
- Direct links to AWS Console

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 Roadmap

See [CHANGELOG.md](CHANGELOG.md) for version history and upcoming features:

- **v3.0 (Site)**: Static site deployment
- **v10.0 (Product)**: Full production release with payment integration

---

## 🐛 Issues & Support

For bugs, feature requests, or questions:
- Open an issue on GitHub
- Contact via Telegram: @debugger00

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Etherscan for blockchain data API
- TronScan for Tron network data
- FastAPI for the excellent web framework
- Nginx for high-performance static serving

---

*Built with ❤️ for the blockchain community*
