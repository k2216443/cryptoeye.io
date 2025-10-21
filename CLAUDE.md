# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ChainEye is a blockchain wallet security analysis platform that evaluates risk for Ethereum (ERC20) and Tron (TRC20) wallet addresses. The system provides real-time security scoring through a FastAPI backend, static website frontend, and Telegram bot integration.

## Development Commands

### Local Development

**Run API Server:**
```bash
cd src/api
python main.py
# API runs on http://localhost:8000
```

**Run Single Test:**
```bash
cd src/api
python test_eth.py   # Test Ethereum scoring
python test_trc.py   # Test Tron scoring
```

**Install Dependencies:**
```bash
cd src/api
pip install -r requirements.txt
```

### Docker Operations

**Build and Run API Container:**
```bash
cd src/api
docker build -t chaineye-api:latest .
docker run -p 8000:8000 -e ETHERSCAN_API_KEY=your_key chaineye-api:latest
```

**Build and Run Static Site:**
```bash
cd src/static
docker build -t chaineye-site:latest .
docker run -p 8080:8080 chaineye-site:latest
```

**Run Full Stack with Docker Compose:**
```bash
docker-compose up -d       # Start all services
docker-compose logs -f     # View logs
docker-compose down        # Stop all services
```

Note: API runs on port 8000, static site on port 8080 in docker-compose.

### Infrastructure & Deployment

**Terraform:**
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**Check Build Version:**
```bash
cat version  # Current version (v2.0)
```

The CI/CD pipeline automatically triggers on git push via AWS CodeBuild (see `buildspec.yaml`). It builds both API and static site containers, pushes to ECR with versioning format `v{VERSION}-{GIT_COMMIT}`, and sends Telegram notifications on success/failure.

## Architecture

### Multi-Service Design

ChainEye uses a microservices architecture with three main components:

1. **FastAPI Backend** (`src/api/`): Handles wallet security evaluation
2. **Nginx Static Site** (`src/static/`): Serves web interface, proxies API requests
3. **Telegram Bot**: Provides wallet analysis through messaging interface

### API Structure (`src/api/`)

**Entry Point:**
- `main.py` - FastAPI application with 3 endpoints:
  - `/health` - Health check
  - `/api/evaluate?addr=0x...` - Evaluate wallet (query param)
  - `/api/wallet/{addr}` - Evaluate wallet (path param)
  - `/api/tg` - Telegram webhook handler

**Scoring Engines:**
- `scorer_etherscan/` - Ethereum wallet analysis
  - `scorer.py` - Core scoring logic with WalletScorer class
  - `rules.py` - Risk rules (empty wallet, age, inactivity, fail ratio, dust, etc.)
  - `eth_client.py` - Etherscan API client
  - `formatter.py` - Output formatting
  - `config.py` - BASE_SCORE and thresholds

- `scorer_tron/` - Tron wallet analysis
  - `scorer.py` - Core scoring logic with WalletScorerTRC class
  - `rules.py` - Risk rules adapted for TRC20
  - `trc_client.py` - TronScan API client
  - Parallel structure to scorer_etherscan

**Providers:**
- `providers/etherscan.py` - Main Etherscan integration class
- `providers/etherscan2.py` - Alternative/extended provider

**Libraries:**
- `libs/log.py` - JSON structured logging
- `libs/tg.py` - Telegram bot client (TelegramBot class)
- `libs/format.py` - Security message formatting

### Scoring System

Both scoring engines use a rule-based evaluation system:

1. Start with BASE_SCORE (default 100 or configurable)
2. Apply penalty rules that deduct points:
   - Empty wallet detection
   - No transaction history
   - Wallet age (newer = riskier)
   - Inactivity period
   - Failed transaction ratio
   - Low unique counterparties
   - Dust amounts (ETH/TRX or tokens)
   - Token-only empty wallets
   - Contract verification status
   - Proxy contracts
3. Clamp final score to 0-100 range
4. Assign risk tier: critical (<20), high (<40), medium (<70), low (<90), very_low (>=90)

Results include:
- Numeric score
- Risk tier
- List of Reason objects (rule name, penalty, description, metadata)
- Metrics dictionary with transaction counts, balances, dates

### Logging & Monitoring

All services use JSON structured logging with fields:
- `asctime` - Timestamp
- `level` - Log level
- `name` - Logger name
- `message` - Log message
- `event` - Event type (e.g., "wallet_evaluation", "trace_request")
- `request_id` - Optional correlation ID from headers

Log files: `/var/log/cryptoeye.json.log` (configurable via LOG_FILE env var)

### Environment Variables

Required in `src/api/.env` or docker-compose `.env`:
- `ETHERSCAN_API_KEY` - Etherscan API key (required)
- `BOT_TOKEN` - Telegram bot token (optional, for bot features)
- `LOG_LEVEL` - Logging level (default: INFO)
- `LOG_FILE` - Log file path (default: /var/log/cryptoeye.json.log)

### Port Configuration

Development:
- API: 8000 (main.py runs on 0.0.0.0:8000)

Docker Compose:
- API: 8000
- Static site: 8080 (nginx proxies /api/* to api:8000)

Production (AWS):
- ALB handles SSL termination and routing
- Internal containers likely use same ports

### Nginx Configuration

Two nginx configs in `src/static/`:
- `nginx.conf` - Production config (proxies to 127.0.0.1:8000)
- `nginx.docker-compose.conf` - Local development (proxies to api:8000 via container networking)

Docker Compose mounts the appropriate config file.

### Infrastructure (AWS/Terraform)

Key resources in `terraform/`:
- ECR repositories: `cryptoeye` (API) and `chaineye-site` (static)
- CodeBuild: CI/CD pipeline defined in `buildspec.yaml`
- Load Balancer (ALB): Routes traffic to services
- EC2: Likely hosts for running containers
- Route53: DNS for chaineye.io domain
- S3: Terraform state backend in `terraform/bucket/`

Terraform modules:
- `modules/codebuild/` - CI/CD setup
- `modules/lb/` - Load balancer configuration
- `modules/ec2/` - EC2 instance configuration

## Key Design Patterns

### Async Processing
- FastAPI uses `anyio.to_thread.run_sync()` to run blocking scorer operations in thread pool
- Prevents blocking event loop during Etherscan/TronScan API calls

### Address Validation
- Ethereum: Regex `^0x[a-fA-F0-9]{40}$`
- Tron: Starts with "T" (validated in scanner logic)

### Error Handling
- API errors return score of 20 with "api_error" reason
- Graceful degradation when blockchain APIs fail

### Telegram Integration
- `/api/tg` endpoint receives webhook from Telegram
- Extracts address from message text
- Validates address format
- Calls Etherscan evaluator
- Formats response with HTML
- Sends back to chat

### Version Management
- Version stored in `version` file (currently v2.0)
- Git commit hash appended during build: `v2.0-abc1234`
- Both containers tagged with same version
- CHANGELOG.md tracks feature releases

## Testing Strategy

Manual test scripts provided:
- `src/api/test_eth.py` - Test Ethereum address evaluation
- `src/api/test_trc.py` - Test Tron address evaluation
- `src/api/test.sh` - Shell script for testing (check contents for usage)

No automated test suite currently exists. Tests involve calling the evaluate endpoints with known addresses.

## Important Notes

- The API client in `main.py` uses `app.state.scanner` to share a single Etherscan instance across requests (lifespan context manager)
- The docker-compose setup requires `.env` file at project root with required environment variables
- Static site serves from `/` and proxies API requests from `/api/*` to backend
- Buildspec sends Telegram notifications on all build events (success, failure, push errors)
- Security headers redacted in logs: authorization, cookie, x-api-key
- Request body JSON is redacted for sensitive fields in trace logging
