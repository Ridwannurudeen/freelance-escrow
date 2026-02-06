# Zero to GenLayer: Freelance Escrow dApp

A hands-on tutorial and complete dApp for building a trustless freelance escrow on GenLayer, where AI validators evaluate work quality and release payments automatically.

## What This Is

This project accompanies the **"Zero to GenLayer"** tutorial — a multi-part guide that takes developers from zero blockchain experience to building a fully functional GenLayer dApp.

The Freelance Escrow contract demonstrates GenLayer's key innovations:
- **Optimistic Democracy** — A jury of AI validators reaches consensus on subjective decisions
- **Equivalence Principle** — Validators don't need identical answers, just equivalent verdicts
- **Native Web Access** — Contracts fetch live web content without oracles
- **LLM-Powered Evaluation** — AI judges whether freelance work meets requirements

## How It Works

1. Client posts a job with requirements and locks payment in the contract
2. Freelancer accepts the job and submits their deliverable (a URL)
3. AI validators independently fetch the submission and evaluate it
4. Payment releases to the freelancer (approved) or refunds to the client (rejected)

No middlemen. No dispute tickets. No "Trust & Safety" teams.

## Project Structure

```
freelance-escrow/
├── contracts/
│   └── freelance_escrow.py          # The AI-powered escrow contract
├── app/
│   └── src/
│       ├── components/
│       │   └── EscrowScreen.vue     # Main UI component
│       ├── logic/
│       │   └── FreelanceEscrow.js   # Contract interaction wrapper
│       └── services/
│           └── genlayer.js          # Client/account setup
├── test/
│   └── test_freelance_escrow.py     # Contract tests (10 test cases)
├── deploy/
│   └── deployScript.ts              # Deployment script
├── zero-to-genlayer-tutorial.md     # The full tutorial
└── genlayer-cheatsheet.md           # Quick reference guide
```

## Quick Start

### Prerequisites
- Docker (v26+)
- Node.js (v18+)
- GenLayer CLI (`npm install -g genlayer`)

### Setup

```bash
# Clone this repo
git clone https://github.com/Ridwannurudeen/freelance-escrow.git
cd freelance-escrow

# Start GenLayer Studio
genlayer init
genlayer up

# Install dependencies
npm install
cd app && npm install
```

### Deploy the Contract

```bash
genlayer deploy --contract contracts/freelance_escrow.py \
  --args "Build a Landing Page" \
  "Create a responsive landing page with hero section, features grid, and contact form" \
  "72"
```

### Run the Frontend

```bash
# Copy .env and add your contract address
cp app/.env.example app/.env
# Edit app/.env with your deployed contract address

cd app
npm run dev
```

Open `http://localhost:5173` to interact with the escrow dApp.

### Run Tests

```bash
genlayer test
```

## Tutorial

Read the full tutorial: [zero-to-genlayer-tutorial.md](./zero-to-genlayer-tutorial.md)

**Parts:**
1. The Tech Behind the Magic (Optimistic Democracy, Equivalence Principle)
2. Setting Up GenLayer Studio
3. Building the Escrow Contract
4. The Frontend with genlayer-js
5. Testing Your Contract
6. Deploying to Testnet

## Tech Stack

- **Contract:** Python + GenLayer SDK (`from genlayer import *`)
- **Frontend:** Vue.js 3 + Vite + Tailwind CSS
- **SDK:** genlayer-js
- **Testing:** gltest

## Resources

- [GenLayer Docs](https://docs.genlayer.com)
- [GenLayer Studio](https://github.com/genlayerlabs/genlayer-studio)
- [genlayer-js SDK](https://github.com/genlayerlabs/genlayer-js)
- [GenLayer Discord](https://discord.gg/genlayer)

## License

MIT
