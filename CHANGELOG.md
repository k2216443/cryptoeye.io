# Changelog

All notable changes to ChainEye.io will be documented in this file.

---

## [v10.0] - Product

**Codename:** Product

### Telegram
- [ ] Working on full text messages and finds TRC20 and ERC20 addresses
- [x] Nice Message Style

### Core
- [ ] Working with ERC20 (Ethereum) and TRC20 support
- [ ] Rate limiting (5 requests per day)
- [ ] Payment logic (50 requests per day for paid tier)

### Website
- [ ] Site deployed at `https://chaineye.io`
- [ ] Client account with plain authorization
- [ ] Telegram ID binding

---

## [v3.0] - Site

**Codename:** Site

### Website
- [x] Static site redesign with ChainEye brand identity
  - Dark navy/blue gradient background with cyan accents
  - Glassmorphism design with backdrop blur effects
  - Modern, animated UI components (fade-ins, slide-ups, glowing effects)
  - Mobile-responsive design with optimized breakpoints
- [x] Landing page (index.html)
  - Wallet address input with real-time validation
  - Blockchain network detection (Ethereum/Tron)
  - Interactive example addresses
  - "Instant Audit" call-to-action button
- [x] Security report page (evaluate.html)
  - Risk score visualization with animated glowing circles
  - Color-coded risk levels (green/orange/red)
  - Security indicators with hover effects
  - Wallet details presentation
  - Error and loading states
- [x] Brand assets integration
  - ChainEye logo and imagery
  - Consistent color scheme (#0a1628, #00d9ff)
- [ ] Site deployed at `https://chaineye.io`

### Infrastructure
- [x] Static site containerization
  - Dockerfile with nginx:alpine base
  - Nginx configuration with JSON logging
  - API reverse proxy to backend (port 8080)
  - Optimized for production deployment
- [x] ECR repository for static site (chaineye-site)
- [x] Dual container build pipeline
  - API container (cryptoeye)
  - Static site container (chaineye-site)
  - Unified versioning with git tags
- [x] IAM permissions for multi-container deployment

### CI/CD
- [x] Enhanced Telegram notifications
  - Rich HTML formatting with emojis
  - Success notifications with build details
  - Failure notifications with specific error context
  - Clickable links to AWS CodeBuild console
  - Commit message and author information
- [x] Push failure detection
  - Individual status tracking per image
  - Detailed error reporting
  - Proper exit codes for failed deployments
- [x] Buildspec improvements
  - Build both API and static site images
  - JSON-formatted logs
  - Automated deployment notifications

---

## [v2.0] - PoC

**Codename:** Proof of Concept

### Telegram
- [x] Working on plan for ERC20 only
- [x] Nice message styling

### Core
- [x] ERC20 address support (Ethereum blockchain only)

---

## Features

### Wallet Discovery
- Find wallets related to:
  - Ukraine
  - Russia
  - Iraq