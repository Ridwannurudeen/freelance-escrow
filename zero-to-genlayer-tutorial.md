# Zero to GenLayer: Building a Trustless Freelance Escrow

*A hands-on tutorial for developers who want to build smart contracts that can actually think.*

---

## The 3 AM Problem

It's 3 AM. You're staring at a Upwork dispute that's been open for two weeks.

You hired a developer to build a React dashboard. They delivered... something. It loads. It has buttons. But half the features from the spec are missing, the code looks like it was written during an earthquake, and now you're playing email ping-pong with a "Trust & Safety" team on the other side of the planet.

Here's the thing: **both of you are technically right.** They delivered code. You expected quality code. The spec said "dashboard with user analytics"—it didn't define what "good" looks like.

Traditional smart contracts can't help here. They're calculators. They can verify "did wallet A send 1 ETH to wallet B?" but they can't answer "is this code any good?"

That's the **Subjectivity Problem**. And until now, crypto couldn't touch it.

Enter GenLayer.

---

## What We're Building

By the end of this tutorial, you'll have built a **Freelance Escrow dApp** where:

1. A client posts a job with requirements and locks payment in the contract
2. A freelancer accepts and submits their work (a GitHub repo URL)
3. The contract *actually reads the repo* and uses AI to evaluate if it meets requirements
4. Payment releases automatically—or doesn't—based on the verdict

No middleman. No dispute tickets. No "Trust & Safety" team.

**Tech stack:**
- GenLayer Studio (local development)
- Python (Intelligent Contract)
- Vue.js + Vite + genlayer-js (frontend)
- Your sanity (optional but recommended)

Let's go.

---

# Part 1: The Tech Behind the Magic

## Why Traditional Smart Contracts Can't Judge Quality

Ethereum's EVM is deterministic by design. Every node runs the same code, gets the same result. That's the whole point—trustless verification.

But determinism has a cost: **rigidity**.

```
// This works on Ethereum
if (block.timestamp > deadline) {
    release(funds);
}

// This doesn't (and never will)
if (work.quality >= "acceptable") {  // ← What does this even mean?
    release(funds);
}
```

You can't ask the EVM "is this code good?" because:
1. "Good" is subjective
2. Fetching external data requires oracles (Chainlink, etc.)
3. Even with oracles, you get data—not judgment

GenLayer flips this model entirely.

---

## Optimistic Democracy: A Jury of LLMs

Think of GenLayer like this:

> **Ethereum** = A calculator. Always gives the same answer. Can't handle opinions.
>
> **GenLayer** = A jury of LLMs. Each has their own perspective, but they vote on truth.

Here's how it actually works:

### Step 1: You Submit a Transaction
You call a contract method that requires judgment—like "evaluate this GitHub repo."

### Step 2: A Leader is Chosen
GenLayer randomly picks one validator to be the "Leader." This validator runs the transaction first—fetching the URL, calling the LLM, getting a result.

### Step 3: Other Validators Check the Work
Four more validators independently run the same transaction. They fetch the same URL, ask their own LLMs, get their own results.

**Here's the key insight:** They don't need identical answers. They need *equivalent* answers.

### Step 4: Consensus via Equivalence
If the Leader says "Yes, the work is complete" and 3 out of 4 validators agree (even if their reasoning differs), the transaction passes.

If there's disagreement? The transaction can be appealed, bringing in more validators until consensus is reached.

```
┌─────────────────────────────────────────────────────────────┐
│                    OPTIMISTIC DEMOCRACY                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Transaction Submitted                                     │
│           │                                                 │
│           ▼                                                 │
│   ┌───────────────┐                                         │
│   │    Leader     │ ──► Executes first, proposes result     │
│   │   (1 of 5)    │                                         │
│   └───────────────┘                                         │
│           │                                                 │
│           ▼                                                 │
│   ┌───────────────────────────────────────┐                 │
│   │         Other Validators (4)          │                 │
│   │  Each runs independently with own LLM │                 │
│   └───────────────────────────────────────┘                 │
│           │                                                 │
│           ▼                                                 │
│   ┌───────────────────────────────────────┐                 │
│   │      EQUIVALENCE PRINCIPLE CHECK      │                 │
│   │  "Are results equivalent, not equal?" │                 │
│   └───────────────────────────────────────┘                 │
│           │                                                 │
│     ┌─────┴─────┐                                           │
│     ▼           ▼                                           │
│  ✅ PASS     ❌ FAIL → Appeal with more validators          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## The Equivalence Principle: Same-Same but Different

This is the part that makes GenLayer click.

In traditional consensus, validators must produce **identical** outputs. `2 + 2 = 4` on every node, every time.

But when you ask an LLM "is this code good?", you might get:
- Validator A: "Yes, it meets all requirements and follows best practices."
- Validator B: "Approved. The implementation is solid."
- Validator C: "The code fulfills the spec adequately."

Different words. Same verdict. **Equivalent.**

GenLayer lets you, the developer, define what "equivalent" means for your contract:

```python
@gl.equivalence_principle(
    "Results are equivalent if they agree on the final verdict "
    "(approved/rejected) regardless of the specific reasoning provided."
)
def evaluate_submission(self):
    # Your evaluation logic here
```

This is the secret sauce. You're not asking for identical outputs—you're asking: "Do these validators fundamentally agree?"

**Real-world analogy:** If you ask five movie critics "Is The Godfather good?", they'll give different reviews. But they'll all say yes. That's equivalence.

---

## Why This Matters for Our Escrow

Back to our Freelance Escrow:

| Traditional Approach | GenLayer Approach |
|---------------------|-------------------|
| Escrow holds funds | Same |
| Freelancer submits link | Same |
| Human arbitrator reviews | **AI validators review** |
| Days/weeks of dispute | **Seconds of consensus** |
| Trust the platform | **Trust the protocol** |

The contract doesn't just hold money. It *judges work*. And it does it in a way that's:
- Decentralized (multiple validators)
- Trustless (no single point of failure)
- Fast (consensus in seconds, not days)

Let's build it.

---

# Part 2: Setting Up GenLayer Studio

## Prerequisites

Before we start, make sure you have:

- **Docker** (v26+) — [Install Docker](https://docs.docker.com/get-docker/)
- **Node.js** (v18+) — [Install Node](https://nodejs.org/)
- A code editor (VS Code recommended)
- Coffee (non-optional)

## Installing the GenLayer CLI

Open your terminal and run:

```bash
npm install -g genlayer
```

Verify the installation:

```bash
genlayer --version
```

## Starting GenLayer Studio

GenLayer Studio is your local sandbox. It simulates the entire GenLayer network on your machine—validators, LLMs, consensus, everything.

```bash
genlayer init
genlayer up
```

This pulls the Docker images and starts the environment. First run takes a few minutes. Go refill that coffee.

Once it's ready, open your browser to:

```
http://localhost:8080
```

You should see the GenLayer Studio interface:

```
┌─────────────────────────────────────────────────────────────┐
│  GenLayer Studio                                            │
├──────────────────┬──────────────────────────────────────────┤
│                  │                                          │
│  📁 Contracts    │   // Your code editor                    │
│  ├── examples/   │   // appears here                        │
│  └── my_first.py │                                          │
│                  │                                          │
├──────────────────┼──────────────────────────────────────────┤
│  ▶️ Deploy       │   Output / Logs                          │
│  🔧 Interact     │                                          │
│                  │                                          │
└──────────────────┴──────────────────────────────────────────┘
```

---

## Your First Contract: Hello GenLayer

Let's make sure everything works before building the escrow.

In the Studio, create a new file called `hello.py`:

```python
from genlayer import *

@gl.contract
class HelloGenLayer:
    greeting: str
    
    def __init__(self):
        self.greeting = "Hello from GenLayer!"
    
    @gl.public.view
    def get_greeting(self) -> str:
        return self.greeting
    
    @gl.public.write
    def set_greeting(self, new_greeting: str):
        self.greeting = new_greeting
```

Hit **Deploy**. If you see a success message and a contract address, you're ready.

**⚠️ Watch out:** If Docker isn't running, you'll get cryptic connection errors. Always check `docker ps` first.

---

# Part 3: Building the Escrow Contract

Now the real fun begins. We're building a contract that:
1. Stores job details and requirements
2. Locks client funds
3. Accepts freelancer submissions
4. **Uses AI to evaluate if the work meets requirements**
5. Releases or refunds based on the verdict

## Contract Structure

```python
# freelance_escrow.py
from genlayer import *
import json

@gl.contract
class FreelanceEscrow:
    """
    A trustless escrow that uses GenLayer's AI validators to 
    evaluate if freelance work meets the client's requirements.
    
    No middlemen. No disputes. Just code.
    """
    
    # ============================================
    # STATE VARIABLES
    # ============================================
    
    # Job details
    client: Address           # Who posted the job
    freelancer: Address       # Who accepted it
    job_title: str            # "Build React Dashboard"
    requirements: str         # Detailed requirements
    payment_amount: u256      # Locked funds (in wei)
    submission_url: str       # Freelancer's deliverable URL
    
    # Status tracking
    status: str               # "open", "in_progress", "submitted", "completed", "refunded"
    created_at: u256          # Timestamp
    deadline: u256            # Unix timestamp for deadline
    
    # ============================================
    # CONSTRUCTOR
    # ============================================
    
    def __init__(
        self, 
        job_title: str, 
        requirements: str, 
        deadline_hours: u256
    ):
        """
        Client creates a new escrow job.
        Payment is sent with this transaction and locked.
        """
        self.client = gl.message.sender
        self.freelancer = Address("")  # Empty until accepted
        self.job_title = job_title
        self.requirements = requirements
        self.payment_amount = gl.message.value
        self.submission_url = ""
        self.status = "open"
        self.created_at = gl.block.timestamp
        self.deadline = gl.block.timestamp + (deadline_hours * 3600)
        
        # Must send payment when creating
        assert gl.message.value > 0, "Must include payment"
    
    # ============================================
    # FREELANCER ACTIONS
    # ============================================
    
    @gl.public.write
    def accept_job(self):
        """
        Freelancer accepts the job. 
        Only one freelancer can accept.
        """
        assert self.status == "open", "Job not available"
        assert gl.message.sender != self.client, "Client can't accept own job"
        
        self.freelancer = gl.message.sender
        self.status = "in_progress"
    
    @gl.public.write
    def submit_work(self, url: str):
        """
        Freelancer submits their deliverable URL.
        This could be a GitHub repo, hosted app, Google Doc, etc.
        """
        assert self.status == "in_progress", "Job not in progress"
        assert gl.message.sender == self.freelancer, "Only freelancer can submit"
        assert len(url) > 0, "URL cannot be empty"
        
        self.submission_url = url
        self.status = "submitted"
    
    # ============================================
    # THE MAGIC: AI-POWERED EVALUATION
    # ============================================
    
    @gl.public.write
    @gl.equivalence_principle(
        "Two evaluations are equivalent if they reach the same "
        "final verdict (APPROVED or REJECTED). The specific "
        "reasoning or score may differ, but the binary outcome "
        "must match."
    )
    async def evaluate_and_release(self):
        """
        This is where GenLayer shines.
        
        The contract:
        1. Fetches the submission URL
        2. Asks AI to evaluate against requirements
        3. Releases payment if approved, refunds if rejected
        
        Multiple validators run this independently and must 
        reach equivalent conclusions.
        """
        assert self.status == "submitted", "No submission to evaluate"
        
        # Step 1: Fetch the submission
        # GenLayer can natively access the web - no oracles needed!
        submission_content = await gl.get_webpage(
            self.submission_url,
            mode="text"  # Get text content of the page
        )
        
        # Step 2: Build the evaluation prompt
        evaluation_prompt = f"""
You are evaluating a freelance submission for a job.

JOB TITLE: {self.job_title}

REQUIREMENTS:
{self.requirements}

SUBMISSION URL: {self.submission_url}

SUBMISSION CONTENT:
{submission_content[:5000]}  # Limit to avoid token overflow

TASK:
Evaluate whether this submission meets the requirements.
Consider:
1. Does it address all stated requirements?
2. Is the implementation functional?
3. Are there any critical missing pieces?

RESPOND WITH EXACTLY ONE OF:
- APPROVED: if the submission reasonably meets the requirements
- REJECTED: if the submission fails to meet key requirements

Then provide a brief explanation (2-3 sentences max).

Your response format:
VERDICT: [APPROVED/REJECTED]
REASON: [Your explanation]
"""
        
        # Step 3: Ask the AI to evaluate
        # Each validator's LLM will process this independently
        ai_response = await gl.call_llm(evaluation_prompt)
        
        # Step 4: Parse the verdict
        verdict = "REJECTED"  # Default to rejected for safety
        if "VERDICT: APPROVED" in ai_response.upper():
            verdict = "APPROVED"
        elif "VERDICT: REJECTED" in ai_response.upper():
            verdict = "REJECTED"
        
        # Step 5: Execute based on verdict
        if verdict == "APPROVED":
            # Transfer payment to freelancer
            gl.transfer(self.freelancer, self.payment_amount)
            self.status = "completed"
        else:
            # Refund to client
            gl.transfer(self.client, self.payment_amount)
            self.status = "refunded"
        
        # Return result for transparency
        return {
            "verdict": verdict,
            "evaluation": ai_response
        }
    
    # ============================================
    # SAFETY MECHANISMS
    # ============================================
    
    @gl.public.write
    def cancel_job(self):
        """
        Client can cancel if no freelancer accepted yet.
        """
        assert self.status == "open", "Can only cancel open jobs"
        assert gl.message.sender == self.client, "Only client can cancel"
        
        gl.transfer(self.client, self.payment_amount)
        self.status = "refunded"
    
    @gl.public.write
    def claim_deadline_refund(self):
        """
        Client can claim refund if deadline passed without submission.
        """
        assert gl.block.timestamp > self.deadline, "Deadline not passed"
        assert self.status in ["open", "in_progress"], "Invalid status"
        assert gl.message.sender == self.client, "Only client can claim"
        
        gl.transfer(self.client, self.payment_amount)
        self.status = "refunded"
    
    # ============================================
    # VIEW METHODS (Read-only)
    # ============================================
    
    @gl.public.view
    def get_job_details(self) -> dict:
        """Get all job information."""
        return {
            "title": self.job_title,
            "requirements": self.requirements,
            "payment": str(self.payment_amount),
            "client": str(self.client),
            "freelancer": str(self.freelancer),
            "status": self.status,
            "submission_url": self.submission_url,
            "deadline": str(self.deadline)
        }
    
    @gl.public.view
    def get_status(self) -> str:
        """Quick status check."""
        return self.status
```

---

## Code Walkthrough: The Important Bits

### The Equivalence Principle Decorator

```python
@gl.equivalence_principle(
    "Two evaluations are equivalent if they reach the same "
    "final verdict (APPROVED or REJECTED)..."
)
async def evaluate_and_release(self):
```

This decorator tells validators how to compare their results. We're saying: "I don't care if Validator A writes a 500-word essay and Validator B writes two sentences. If they both say APPROVED, that's consensus."

**🔥 Pro tip:** Keep your equivalence criteria simple and binary when possible. "Approved vs Rejected" is much easier to reach consensus on than "score from 1-100."

### Native Web Access

```python
submission_content = await gl.get_webpage(
    self.submission_url,
    mode="text"
)
```

This is GenLayer flexing. No Chainlink. No API keys. No oracle networks. The contract just... reads the web. Each validator fetches the URL independently, ensuring no single point of failure.

**⚠️ Watch out:** Web content can change. If the freelancer updates their submission between validators fetching it, you might get inconsistent results. For production, consider requiring IPFS links or commit hashes.

### LLM Calls

```python
ai_response = await gl.call_llm(evaluation_prompt)
```

Each validator has its own LLM (could be GPT-4, Claude, Llama, etc.). They all process the same prompt but may generate different responses. That's fine—we only care about the verdict matching.

**🔥 Pro tip:** Structure your prompts to force specific output formats. "VERDICT: APPROVED" is much easier to parse reliably than free-form responses.

---

## Deploying the Contract

In GenLayer Studio:

1. Paste the contract code
2. Set constructor parameters:
   - `job_title`: "Build React Dashboard"
   - `requirements`: "Create a React dashboard with: 1) User authentication, 2) Analytics charts using Recharts, 3) Responsive design, 4) Dark mode toggle"
   - `deadline_hours`: 72
3. Set the **value** (payment amount in wei)
4. Click **Deploy**

Note your contract address—you'll need it for the frontend.

---

# Part 4: The Frontend with genlayer-js

Time to build the UI. We'll use the GenLayer boilerplate (Vue.js + Vite + Tailwind) and the official GenLayer JavaScript SDK.

## Project Setup

Scaffold a new project with the GenLayer CLI:

```bash
genlayer new freelance-escrow
cd freelance-escrow
```

This gives you a complete project structure:

```
freelance-escrow/
├── contracts/          # Python intelligent contracts go here
├── app/                # Vue.js frontend
│   └── src/
│       ├── components/ # UI components
│       ├── logic/      # Contract interaction wrappers
│       └── services/   # GenLayer client setup
├── test/               # Contract tests
├── deploy/             # Deployment scripts
└── tools/              # Helper utilities
```

Copy your `freelance_escrow.py` contract into `contracts/`, then install frontend dependencies:

```bash
cd app
npm install
```

## Configure the Client

The boilerplate already includes `app/src/services/genlayer.js`:

```javascript
// app/src/services/genlayer.js
import { createClient, createAccount as createGenLayerAccount, generatePrivateKey } from "genlayer-js";
import { simulator } from "genlayer-js/chains";

const accountPrivateKey = localStorage.getItem("accountPrivateKey")
  ? localStorage.getItem("accountPrivateKey")
  : null;
export const account = accountPrivateKey ? createGenLayerAccount(accountPrivateKey) : null;

export const createAccount = () => {
  const newAccountPrivateKey = generatePrivateKey();
  localStorage.setItem("accountPrivateKey", newAccountPrivateKey);
  return createGenLayerAccount(newAccountPrivateKey);
};

export const removeAccount = () => {
  localStorage.removeItem("accountPrivateKey");
};

export const client = createClient({ chain: simulator, account });
```

This handles wallet creation, persistence via `localStorage`, and client setup. For local development, it connects to the GenLayer Studio simulator.

**Warning:** The `simulator` chain is for local development only. For testnet, use `testnetAsimov` from `genlayer-js/chains`.

## Building the Contract Logic Layer

Create a wrapper class that handles all contract interactions. This keeps your components clean:

```javascript
// app/src/logic/FreelanceEscrow.js
import { createClient } from "genlayer-js";
import { simulator } from "genlayer-js/chains";

class FreelanceEscrow {
  contractAddress;
  client;

  constructor(contractAddress, account = null, studioUrl = null) {
    this.contractAddress = contractAddress;
    const config = {
      chain: simulator,
      ...(account ? { account } : {}),
      ...(studioUrl ? { endpoint: studioUrl } : {}),
    };
    this.client = createClient(config);
  }

  updateAccount(account) {
    this.client = createClient({ chain: simulator, account });
  }

  async getJobDetails() {
    return await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_job_details",
      args: [],
    });
  }

  async getStatus() {
    return await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_status",
      args: [],
    });
  }

  async getEvaluation() {
    return await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_evaluation",
      args: [],
    });
  }

  async acceptJob() {
    const txHash = await this.client.writeContract({
      address: this.contractAddress,
      functionName: "accept_job",
      args: [],
    });
    return await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: "FINALIZED",
      interval: 10000,
    });
  }

  async submitWork(url) {
    const txHash = await this.client.writeContract({
      address: this.contractAddress,
      functionName: "submit_work",
      args: [url],
    });
    return await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: "FINALIZED",
      interval: 10000,
    });
  }

  async evaluateAndRelease() {
    const txHash = await this.client.writeContract({
      address: this.contractAddress,
      functionName: "evaluate_and_release",
      args: [],
    });
    return await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: "FINALIZED",
      interval: 10000,
      retries: 30,
    });
  }

  async cancelJob() {
    const txHash = await this.client.writeContract({
      address: this.contractAddress,
      functionName: "cancel_job",
      args: [],
    });
    return await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: "FINALIZED",
      interval: 10000,
    });
  }
}

export default FreelanceEscrow;
```

## Building the Escrow Component

Now the main UI. Vue's reactive system makes it easy to keep the UI in sync with contract state:

```vue
<!-- app/src/components/EscrowScreen.vue -->
<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <!-- Header with wallet connection -->
    <header class="bg-white shadow">
      <div class="max-w-4xl mx-auto py-6 px-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold">Freelance Escrow</h1>
        <div>
          <button v-if="!userAddress" @click="createUserAccount"
            class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg text-sm">
            Connect Wallet
          </button>
          <div v-else class="flex items-center gap-4">
            <span class="text-sm text-gray-500">{{ userAddress.slice(0, 8) }}...</span>
            <button @click="disconnectUserAccount"
              class="text-sm text-gray-400 hover:text-gray-600">
              Disconnect
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto py-8 px-4">
      <!-- Status Banner -->
      <div :class="statusBannerClass" class="rounded-lg p-4 text-center font-medium text-lg">
        {{ statusLabel }}
      </div>

      <!-- Job Details Card -->
      <div class="bg-white rounded-lg shadow p-6 mt-6 space-y-4">
        <h2 class="text-xl font-semibold">{{ jobDetails.title || "—" }}</h2>

        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-gray-500">Payment</span>
            <p class="font-medium">{{ jobDetails.payment || "0" }} wei</p>
          </div>
          <div>
            <span class="text-gray-500">Status</span>
            <p class="font-medium capitalize">{{ jobDetails.status || "—" }}</p>
          </div>
        </div>

        <div>
          <span class="text-gray-500 text-sm">Requirements</span>
          <p class="mt-1 text-gray-700 bg-gray-50 rounded p-3 text-sm">
            {{ jobDetails.requirements || "—" }}
          </p>
        </div>
      </div>

      <!-- Actions (shown only when wallet is connected) -->
      <div class="bg-white rounded-lg shadow p-6 mt-6" v-if="userAddress">
        <h3 class="text-lg font-medium mb-4">Actions</h3>

        <!-- Accept Job -->
        <button v-if="jobDetails.status === 'open'"
          @click="handleAcceptJob" :disabled="actionLoading"
          class="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300
                 text-white font-medium py-3 px-4 rounded-lg">
          {{ actionLoading ? "Processing..." : "Accept Job" }}
        </button>

        <!-- Submit Work -->
        <div v-if="jobDetails.status === 'in_progress'">
          <input v-model="submissionUrl" type="url"
            placeholder="Enter deliverable URL (GitHub repo, hosted app, etc.)"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg mb-2 text-sm" />
          <button @click="handleSubmitWork"
            :disabled="actionLoading || !submissionUrl"
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300
                   text-white font-medium py-3 px-4 rounded-lg">
            {{ actionLoading ? "Submitting..." : "Submit Work" }}
          </button>
        </div>

        <!-- Trigger AI Evaluation -->
        <button v-if="jobDetails.status === 'submitted'"
          @click="handleEvaluate" :disabled="actionLoading"
          class="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300
                 text-white font-medium py-3 px-4 rounded-lg">
          {{ actionLoading ? "AI is evaluating..." : "Trigger AI Evaluation" }}
        </button>

        <!-- Cancel Job -->
        <button v-if="jobDetails.status === 'open' && userAddress === jobDetails.client"
          @click="handleCancelJob" :disabled="actionLoading"
          class="w-full mt-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-300
                 text-white font-medium py-3 px-4 rounded-lg">
          {{ actionLoading ? "Cancelling..." : "Cancel Job" }}
        </button>
      </div>

      <!-- Evaluation Result -->
      <div v-if="evaluation" class="bg-white rounded-lg shadow p-6 mt-6">
        <h3 class="text-lg font-medium mb-3">AI Evaluation Result</h3>
        <pre class="bg-gray-50 rounded p-4 text-sm whitespace-pre-wrap">{{ evaluation }}</pre>
      </div>

      <!-- Feedback Message -->
      <div v-if="feedbackMessage" :class="feedbackClass" class="rounded-lg p-4 text-sm mt-4">
        {{ feedbackMessage }}
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { account, createAccount, removeAccount } from "../services/genlayer";
import FreelanceEscrow from "../logic/FreelanceEscrow";

const contractAddress = import.meta.env.VITE_CONTRACT_ADDRESS;
const studioUrl = import.meta.env.VITE_STUDIO_URL;
const escrow = new FreelanceEscrow(contractAddress, account, studioUrl);

const userAccount = ref(account);
const userAddress = computed(() => userAccount.value?.address);
const jobDetails = ref({});
const evaluation = ref("");
const actionLoading = ref(false);
const submissionUrl = ref("");
const feedbackMessage = ref("");
const feedbackType = ref("info");

const feedbackClass = computed(() => ({
  "bg-green-100 text-green-800": feedbackType.value === "success",
  "bg-red-100 text-red-800": feedbackType.value === "error",
  "bg-blue-100 text-blue-800": feedbackType.value === "info",
}));

const statusBannerClass = computed(() => {
  const s = jobDetails.value.status;
  if (s === "open") return "bg-blue-100 text-blue-800";
  if (s === "in_progress") return "bg-yellow-100 text-yellow-800";
  if (s === "submitted") return "bg-purple-100 text-purple-800";
  if (s === "completed") return "bg-green-100 text-green-800";
  if (s === "refunded") return "bg-red-100 text-red-800";
  return "bg-gray-100 text-gray-800";
});

const statusLabel = computed(() => {
  const labels = {
    open: "Open — Waiting for a freelancer",
    in_progress: "In Progress — Freelancer is working",
    submitted: "Submitted — Ready for AI evaluation",
    completed: "Completed — Payment released",
    refunded: "Refunded — Payment returned to client",
  };
  return labels[jobDetails.value.status] || "Unknown Status";
});

function showFeedback(message, type = "info") {
  feedbackMessage.value = message;
  feedbackType.value = type;
  setTimeout(() => { feedbackMessage.value = ""; }, 5000);
}

async function loadAll() {
  const [details, evalResult] = await Promise.all([
    escrow.getJobDetails(),
    escrow.getEvaluation(),
  ]);
  jobDetails.value = details instanceof Map ? Object.fromEntries(details) : details;
  evaluation.value = evalResult || "";
}

function createUserAccount() {
  userAccount.value = createAccount();
  escrow.updateAccount(userAccount.value);
}

function disconnectUserAccount() {
  userAccount.value = null;
  removeAccount();
}

async function handleAcceptJob() {
  actionLoading.value = true;
  try {
    await escrow.acceptJob();
    showFeedback("Job accepted!", "success");
    await loadAll();
  } catch (e) {
    showFeedback(`Failed: ${e.message}`, "error");
  }
  actionLoading.value = false;
}

async function handleSubmitWork() {
  actionLoading.value = true;
  try {
    await escrow.submitWork(submissionUrl.value);
    showFeedback("Work submitted!", "success");
    submissionUrl.value = "";
    await loadAll();
  } catch (e) {
    showFeedback(`Failed: ${e.message}`, "error");
  }
  actionLoading.value = false;
}

async function handleEvaluate() {
  actionLoading.value = true;
  try {
    await escrow.evaluateAndRelease();
    showFeedback("Evaluation complete!", "success");
    await loadAll();
  } catch (e) {
    showFeedback(`Failed: ${e.message}`, "error");
  }
  actionLoading.value = false;
}

async function handleCancelJob() {
  actionLoading.value = true;
  try {
    await escrow.cancelJob();
    showFeedback("Job cancelled. Payment refunded.", "success");
    await loadAll();
  } catch (e) {
    showFeedback(`Failed: ${e.message}`, "error");
  }
  actionLoading.value = false;
}

onMounted(() => loadAll());
</script>
```

### Wire It Into App.vue

```vue
<!-- app/src/App.vue -->
<template>
  <Suspense>
    <template #default>
      <EscrowScreen />
    </template>
    <template #fallback>
      <div class="flex items-center justify-center h-screen">
        <div class="text-gray-400">Loading...</div>
      </div>
    </template>
  </Suspense>
</template>

<script setup>
import EscrowScreen from "./components/EscrowScreen.vue";
</script>
```

### Environment Variables

Create `app/.env` with your deployed contract address:

```bash
VITE_CONTRACT_ADDRESS=0x...   # Your deployed contract address
VITE_STUDIO_URL=https://studio.genlayer.com/api
```

## Run It

```bash
cd app
npm run dev
```

Open `http://localhost:5173` and you should see your escrow dApp!

---

## Key genlayer-js Patterns

### Reading Data (Free, No Transaction)

```javascript
const result = await client.readContract({
  address: contractAddress,
  functionName: "get_status",
  args: [],
});
```

### Writing Data (Requires Account, Costs Gas)

```javascript
const hash = await client.writeContract({
  address: contractAddress,
  functionName: "accept_job",
  args: [],
  value: 0n,  // Optional: send funds with the call
});
```

### Waiting for Finality

```javascript
const receipt = await client.waitForTransactionReceipt({
  hash,
  status: "FINALIZED",  // or "ACCEPTED" for faster but less final
});
```

**Pro tip:** Non-deterministic transactions (those using LLMs or web access) take longer to finalize because validators need to reach consensus. Show a loading state!

---

# Part 5: Testing Your Contract

Before you deploy to testnet, let's make sure everything works.

## Test File Structure

The GenLayer boilerplate uses `gltest` for contract testing. Create `test/test_freelance_escrow.py`:

```python
# test/test_freelance_escrow.py
from gltest import get_contract_factory, default_account, get_account
from gltest.assertions import tx_execution_succeeded


def deploy_escrow():
    """Helper to deploy the escrow with standard test parameters."""
    factory = get_contract_factory("FreelanceEscrow")
    contract = factory.deploy(
        args=[
            "Build a Landing Page",
            "Create a responsive landing page with hero section and contact form",
            72,
        ],
        value=1000000,
    )

    # Verify initial state
    status = contract.get_status(args=[])
    assert status == "open"
    return contract


def test_full_flow_with_evaluation():
    """
    Test the complete happy path:
    1. Client creates job with payment
    2. Freelancer accepts
    3. Freelancer submits work
    4. AI evaluates and releases payment
    """
    contract = deploy_escrow()
    freelancer = get_account(1)

    # Freelancer accepts
    result = contract.accept_job(args=[], account=freelancer)
    assert tx_execution_succeeded(result)
    assert contract.get_status(args=[]) == "in_progress"

    # Freelancer submits work
    result = contract.submit_work(
        args=["https://github.com/genlayerlabs/genlayer-studio"],
        account=freelancer,
    )
    assert tx_execution_succeeded(result)
    assert contract.get_status(args=[]) == "submitted"

    # Trigger AI evaluation (may take longer due to LLM consensus)
    result = contract.evaluate_and_release(
        args=[],
        wait_interval=10000,
        wait_retries=30,
    )
    assert tx_execution_succeeded(result)

    final_status = contract.get_status(args=[])
    assert final_status in ["completed", "refunded"]

    # Evaluation should be stored
    evaluation = contract.get_evaluation(args=[])
    assert len(evaluation) > 0


def test_cancel_job():
    """Client can cancel before any freelancer accepts."""
    contract = deploy_escrow()

    result = contract.cancel_job(args=[])
    assert tx_execution_succeeded(result)
    assert contract.get_status(args=[]) == "refunded"


def test_cannot_double_accept():
    """Only one freelancer can accept a job."""
    contract = deploy_escrow()
    freelancer1 = get_account(1)
    freelancer2 = get_account(2)

    # First freelancer accepts
    result = contract.accept_job(args=[], account=freelancer1)
    assert tx_execution_succeeded(result)

    # Second freelancer tries — should fail
    try:
        contract.accept_job(args=[], account=freelancer2)
        assert False, "Should have raised an exception"
    except Exception:
        pass

    assert contract.get_status(args=[]) == "in_progress"
```

## Running Tests

```bash
genlayer test
```

Or run specific tests:

```bash
genlayer test test/test_freelance_escrow.py::test_full_flow_with_evaluation
```

---

# Part 6: Deploying to Testnet

Ready for the real world? Let's deploy to the Asimov testnet.

## Step 1: Switch Networks

```bash
genlayer network
```

Select `testnet-asimov` from the list.

## Step 2: Get Testnet Tokens

You'll need GEN tokens for gas. Get them from the faucet:
- Discord: Join GenLayer's Discord and use the faucet channel
- Or: https://faucet.genlayer.com (if available)

## Step 3: Deploy

```bash
genlayer deploy
```

Follow the prompts to enter constructor arguments.

## Step 4: Update Your Frontend

In `app/src/services/genlayer.js`, switch from the simulator to the testnet chain:

```javascript
import { testnetAsimov } from "genlayer-js/chains";

export const client = createClient({
  chain: testnetAsimov,  // Changed from simulator
  account,
});
```

And in `app/.env`, update the contract address and studio URL:

```bash
VITE_CONTRACT_ADDRESS=0x...   # Your testnet contract address
VITE_STUDIO_URL=               # Leave empty for testnet (uses default RPC)
```

---

# Conclusion: The Gig Economy, Unchained

We just built something that wasn't possible six months ago.

Think about what we've done:
- Created a contract that holds funds
- Made it read live web pages
- Had AI judge whether work meets requirements
- Reached decentralized consensus on a subjective decision
- Released payment automatically

No platform fees. No dispute arbitrators. No "Trust & Safety" teams making $15/hour decisions about your $5,000 project.

This is what GenLayer unlocks: **smart contracts that can think**.

## What's Next?

Here are some ways to extend this project:

1. **Multi-milestone escrow** — Break jobs into chunks with separate evaluations
2. **Reputation system** — Track freelancer success rates on-chain
3. **Appeal mechanism** — Let parties challenge AI verdicts
4. **IPFS integration** — Require permanent, immutable submission URLs
5. **Token-gated jobs** — Only verified freelancers can accept

## Resources

- [GenLayer Documentation](https://docs.genlayer.com)
- [GenLayer Studio GitHub](https://github.com/genlayerlabs/genlayer-studio)
- [genlayer-js SDK](https://github.com/genlayerlabs/genlayer-js)
- [Project Boilerplate](https://github.com/genlayerlabs/genlayer-project-boilerplate)
- [Discord Community](https://discord.gg/genlayer)

## About This Tutorial

This tutorial was written at 2 AM after my fourth cup of coffee and my third failed attempt at getting web scraping to work (turns out I had a typo in the URL).

If you found this useful, share it. If you found bugs, open an issue. If you built something cool with GenLayer, I want to see it.

Now go build something impossible.

---

*Written by a builder, for builders. No AI slop was harmed in the making of this tutorial (okay, maybe a few LLMs were involved).*

**#GenLayer #IntelligentContracts #Web3 #AI #Tutorial**
