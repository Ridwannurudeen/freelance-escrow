# GenLayer Cheat Sheet

*Pin this. You'll need it.*

---

## 🚀 Quick Start Commands

```bash
# Install CLI
npm install -g genlayer

# Start local environment
genlayer init
genlayer up

# Switch networks
genlayer network          # Interactive selector
genlayer network localnet # Direct switch

# Deploy contract
genlayer deploy

# Run tests
genlayer test
genlayer test path/to/test.py::specific_test
```

---

## 📝 Contract Basics

### Minimal Contract

```python
from genlayer import *

@gl.contract
class MyContract:
    value: str
    
    def __init__(self, initial: str):
        self.value = initial
    
    @gl.public.view
    def get_value(self) -> str:
        return self.value
    
    @gl.public.write
    def set_value(self, new_value: str):
        self.value = new_value
```

### State Variable Types

| Type | Example | Notes |
|------|---------|-------|
| `str` | `name: str` | Strings |
| `bool` | `active: bool` | True/False |
| `u256` | `amount: u256` | Unsigned 256-bit int |
| `i256` | `balance: i256` | Signed 256-bit int |
| `Address` | `owner: Address` | Wallet address |
| `bytes` | `data: bytes` | Raw bytes |

### Method Decorators

```python
@gl.public.view      # Read-only, no gas
@gl.public.write     # Modifies state, costs gas
@gl.private          # Internal only
```

---

## 🌐 Web Access (No Oracles!)

```python
# Fetch webpage as text
content = await gl.get_webpage(url, mode="text")

# Fetch as HTML
html = await gl.get_webpage(url, mode="html")

# Fetch JSON API
data = await gl.get_webpage(api_url, mode="json")
```

**⚠️ Watch out:** Web content can change between validator fetches. Use stable URLs (IPFS, commit hashes) for critical data.

---

## 🤖 LLM Calls

```python
# Simple call
response = await gl.call_llm("Your prompt here")

# With system context
response = await gl.call_llm(
    prompt="Analyze this data...",
    system="You are a helpful analyst."
)
```

**🔥 Pro tip:** Structure prompts for parseable output:
```python
prompt = """
Analyze and respond in this EXACT format:
RESULT: [YES/NO]
REASON: [explanation]
"""
```

---

## ⚖️ Equivalence Principle

```python
@gl.equivalence_principle(
    "Results are equivalent if they agree on [SPECIFIC CRITERIA]. "
    "Minor differences in [WHAT'S OKAY TO DIFFER] are acceptable."
)
async def my_method(self):
    # Non-deterministic logic here
    pass
```

**Good equivalence criteria:**
- Binary outcomes: "APPROVED/REJECTED"
- Thresholds: "Score above/below 70"
- Categories: "Same category selected"

**Bad equivalence criteria:**
- Exact text matching
- Precise numerical values
- Subjective quality scores

---

## 💰 Handling Funds

```python
# Receive payment (in constructor or method)
received = gl.message.value

# Transfer funds
gl.transfer(recipient_address, amount)

# Check contract balance
balance = gl.balance(gl.contract.address)
```

---

## 📦 Context Variables

```python
gl.message.sender    # Who called this method
gl.message.value     # ETH/tokens sent with call
gl.block.timestamp   # Current block timestamp
gl.block.number      # Current block number
gl.contract.address  # This contract's address
```

---

## 🔗 genlayer-js Quick Reference

### Setup

```typescript
import { createClient, createAccount } from "genlayer-js";
import { simulator, testnetAsimov } from "genlayer-js/chains";

const client = createClient({ chain: simulator });
const account = createAccount();
```

### Read Contract (Free)

```typescript
const result = await client.readContract({
  address: "0x...",
  functionName: "get_status",
  args: [],
});
```

### Write Contract (Costs Gas)

```typescript
const hash = await client.writeContract({
  account,
  address: "0x...",
  functionName: "do_something",
  args: [arg1, arg2],
  value: 0n,  // Optional: send funds
});
```

### Wait for Confirmation

```typescript
const receipt = await client.waitForTransactionReceipt({
  hash,
  status: "FINALIZED",  // or "ACCEPTED"
});
```

### Deploy Contract

```typescript
const hash = await client.deployContract({
  account,
  code: contractCode,  // Python source as string
  args: [constructorArg1, constructorArg2],
  value: 0n,
});
```

---

## 🧪 Testing Patterns

```python
from genlayer_test import *

def test_my_feature():
    # Get test accounts
    alice = get_account(0)
    bob = get_account(1)
    
    # Deploy
    contract = deploy(
        "my_contract.py",
        "MyContract",
        args=["initial_value"],
        value=1000000,  # Optional: send funds
        account=alice
    )
    
    # Read
    result = contract.get_value()
    assert result == "initial_value"
    
    # Write
    contract.set_value("new_value", account=bob)
    
    # Check for expected errors
    try:
        contract.restricted_method(account=bob)
        assert False, "Should have failed"
    except Exception as e:
        assert "not authorized" in str(e)
```

---

## 🔧 Common Patterns

### Access Control

```python
@gl.public.write
def admin_only(self):
    assert gl.message.sender == self.owner, "Not authorized"
    # ... admin logic
```

### Time Locks

```python
@gl.public.write
def after_deadline(self):
    assert gl.block.timestamp > self.deadline, "Too early"
    # ... logic
```

### State Machine

```python
@gl.public.write  
def next_state(self):
    if self.status == "pending":
        self.status = "active"
    elif self.status == "active":
        self.status = "completed"
    else:
        raise Exception("Invalid state transition")
```

---

## 🐛 Debugging Tips

1. **Check Docker:** `docker ps` - is GenLayer running?
2. **Check logs:** `genlayer logs` for validator output
3. **Reset state:** `genlayer reset` if things get weird
4. **Simplify:** Test with deterministic logic first, add AI later
5. **Print in prompts:** Include "VERDICT:" markers for easy parsing

---

## 📚 Resources

| Resource | URL |
|----------|-----|
| Docs | https://docs.genlayer.com |
| Studio | https://github.com/genlayerlabs/genlayer-studio |
| JS SDK | https://github.com/genlayerlabs/genlayer-js |
| Boilerplate | https://github.com/genlayerlabs/genlayer-project-boilerplate |
| Discord | https://discord.gg/genlayer |

---

*Keep building. Break things. Fix them. Repeat.*
