# freelance_escrow.py
# GenLayer Intelligent Contract: Trustless Freelance Escrow
# 
# This contract demonstrates:
# - Native web access (no oracles needed)
# - LLM-powered evaluation
# - The Equivalence Principle for subjective consensus
#
# Deploy with: genlayer deploy
# Test with:   genlayer test

from genlayer import *
import json


@gl.contract
class FreelanceEscrow:
    """
    A trustless escrow that uses GenLayer's AI validators to 
    evaluate if freelance work meets the client's requirements.
    
    Flow:
    1. Client deploys with job details + payment locked
    2. Freelancer calls accept_job()
    3. Freelancer submits work URL via submit_work()
    4. Anyone calls evaluate_and_release() to trigger AI evaluation
    5. Payment auto-releases to freelancer (approved) or refunds to client (rejected)
    """
    
    # ============================================
    # STATE VARIABLES
    # ============================================
    
    # Job details
    client: Address           # Who posted the job
    freelancer: Address       # Who accepted it (empty until accepted)
    job_title: str            # Human-readable title
    requirements: str         # Detailed requirements for AI to evaluate against
    payment_amount: u256      # Locked funds (in wei)
    submission_url: str       # Freelancer's deliverable URL
    
    # Status tracking
    # Possible values: "open", "in_progress", "submitted", "completed", "refunded"
    status: str
    created_at: u256          # Block timestamp when created
    deadline: u256            # Unix timestamp - deadline for submission
    
    # Evaluation result (stored for transparency)
    evaluation_result: str
    
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
        
        Args:
            job_title: Brief description of the job
            requirements: Detailed requirements (AI will evaluate against these)
            deadline_hours: Hours from now until deadline
        
        Note: Payment is sent with this transaction via gl.message.value
        """
        # Validate inputs
        assert len(job_title) > 0, "Job title required"
        assert len(requirements) > 0, "Requirements required"
        assert deadline_hours > 0, "Deadline must be in the future"
        assert gl.message.value > 0, "Must include payment"
        
        # Set the client as the deployer
        self.client = gl.message.sender
        
        # Initialize empty freelancer (will be set when someone accepts)
        self.freelancer = Address("")
        
        # Store job details
        self.job_title = job_title
        self.requirements = requirements
        self.payment_amount = gl.message.value
        self.submission_url = ""
        
        # Set status and timestamps
        self.status = "open"
        self.created_at = gl.block.timestamp
        self.deadline = gl.block.timestamp + (deadline_hours * 3600)
        
        # Initialize evaluation result
        self.evaluation_result = ""
    
    # ============================================
    # FREELANCER ACTIONS
    # ============================================
    
    @gl.public.write
    def accept_job(self):
        """
        Freelancer accepts the job.
        
        Constraints:
        - Job must be in "open" status
        - Caller cannot be the client (no self-dealing)
        - Only one freelancer can accept
        """
        assert self.status == "open", "Job not available"
        assert gl.message.sender != self.client, "Client cannot accept own job"
        
        self.freelancer = gl.message.sender
        self.status = "in_progress"
    
    @gl.public.write
    def submit_work(self, url: str):
        """
        Freelancer submits their deliverable.
        
        Args:
            url: URL to the deliverable (GitHub repo, hosted app, doc, etc.)
        
        Constraints:
        - Job must be in "in_progress" status
        - Only the assigned freelancer can submit
        - URL cannot be empty
        
        Pro tip: For best results, use stable URLs (GitHub commits, IPFS, etc.)
        """
        assert self.status == "in_progress", "Job not in progress"
        assert gl.message.sender == self.freelancer, "Only assigned freelancer can submit"
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
        "reasoning, wording, or confidence level may differ, "
        "but the binary outcome must match."
    )
    async def evaluate_and_release(self):
        """
        Triggers AI-powered evaluation of the submitted work.
        
        This is where GenLayer shines:
        1. Contract fetches the submission URL (native web access)
        2. AI evaluates whether it meets requirements
        3. Multiple validators run independently and must agree
        4. Payment releases based on consensus verdict
        
        The Equivalence Principle ensures validators don't need
        identical responses - just the same APPROVED/REJECTED verdict.
        
        Returns:
            dict with verdict and full evaluation text
        """
        assert self.status == "submitted", "No submission to evaluate"
        
        # ----------------------------------------
        # Step 1: Fetch the submission content
        # ----------------------------------------
        # GenLayer can natively access the web - no oracles needed!
        # Each validator fetches independently for trustlessness.
        
        try:
            submission_content = await gl.get_webpage(
                self.submission_url,
                mode="text"
            )
        except Exception as e:
            # If we can't fetch the URL, that's a rejection
            self.evaluation_result = f"REJECTED: Could not access submission URL. Error: {str(e)}"
            gl.transfer(self.client, self.payment_amount)
            self.status = "refunded"
            return {"verdict": "REJECTED", "reason": "URL inaccessible"}
        
        # ----------------------------------------
        # Step 2: Build the evaluation prompt
        # ----------------------------------------
        # Structured prompt for consistent, parseable output
        
        evaluation_prompt = f"""You are an impartial evaluator for a freelance job submission.

## JOB DETAILS

**Title:** {self.job_title}

**Requirements:**
{self.requirements}

## SUBMISSION

**URL:** {self.submission_url}

**Content Preview:**
{submission_content[:4000]}

## YOUR TASK

Evaluate whether this submission meets the stated requirements.

Consider:
1. Does it address ALL stated requirements?
2. Is the implementation functional and reasonable?
3. Are there critical missing pieces that would make it unusable?

Be fair but strict. The freelancer was paid to deliver what was asked.

## REQUIRED RESPONSE FORMAT

You MUST respond in exactly this format:

VERDICT: [APPROVED or REJECTED]
CONFIDENCE: [HIGH, MEDIUM, or LOW]
SUMMARY: [One sentence summary of your decision]
DETAILS: [2-3 sentences explaining your reasoning]

Example:
VERDICT: APPROVED
CONFIDENCE: HIGH
SUMMARY: The submission meets all stated requirements.
DETAILS: The code includes user authentication, analytics charts, and responsive design as requested. Dark mode is implemented via a toggle in the header. Code quality is acceptable.
"""
        
        # ----------------------------------------
        # Step 3: Call the LLM
        # ----------------------------------------
        # Each validator's LLM processes this independently.
        # They may use different models (GPT-4, Claude, Llama, etc.)
        
        ai_response = await gl.call_llm(evaluation_prompt)
        
        # ----------------------------------------
        # Step 4: Parse the verdict
        # ----------------------------------------
        # We look for explicit VERDICT markers for reliability
        
        verdict = "REJECTED"  # Default to rejected (safer for client)
        
        response_upper = ai_response.upper()
        if "VERDICT: APPROVED" in response_upper or "VERDICT:APPROVED" in response_upper:
            verdict = "APPROVED"
        elif "VERDICT: REJECTED" in response_upper or "VERDICT:REJECTED" in response_upper:
            verdict = "REJECTED"
        
        # Store the full evaluation for transparency
        self.evaluation_result = ai_response
        
        # ----------------------------------------
        # Step 5: Execute based on verdict
        # ----------------------------------------
        
        if verdict == "APPROVED":
            # Success! Transfer payment to freelancer
            gl.transfer(self.freelancer, self.payment_amount)
            self.status = "completed"
        else:
            # Rejected - refund to client
            gl.transfer(self.client, self.payment_amount)
            self.status = "refunded"
        
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
        Client cancels the job before any freelancer accepts.
        
        Full refund is issued to the client.
        """
        assert self.status == "open", "Can only cancel open jobs"
        assert gl.message.sender == self.client, "Only client can cancel"
        
        gl.transfer(self.client, self.payment_amount)
        self.status = "refunded"
    
    @gl.public.write
    def claim_deadline_refund(self):
        """
        Client claims refund after deadline passes without submission.
        
        This protects clients from freelancers who accept but never deliver.
        """
        assert gl.block.timestamp > self.deadline, "Deadline not yet passed"
        assert self.status in ["open", "in_progress"], "Invalid status for deadline refund"
        assert gl.message.sender == self.client, "Only client can claim deadline refund"
        
        gl.transfer(self.client, self.payment_amount)
        self.status = "refunded"
    
    @gl.public.write
    def withdraw_as_freelancer(self):
        """
        Freelancer withdraws from the job before submitting.
        
        Returns the job to "open" status so another freelancer can accept.
        No penalty - just good faith withdrawal.
        """
        assert self.status == "in_progress", "Can only withdraw from in-progress jobs"
        assert gl.message.sender == self.freelancer, "Only assigned freelancer can withdraw"
        
        self.freelancer = Address("")
        self.status = "open"
    
    # ============================================
    # VIEW METHODS (Read-only, no gas)
    # ============================================
    
    @gl.public.view
    def get_job_details(self) -> dict:
        """Returns all job information as a dictionary."""
        return {
            "title": self.job_title,
            "requirements": self.requirements,
            "payment": str(self.payment_amount),
            "client": str(self.client),
            "freelancer": str(self.freelancer),
            "status": self.status,
            "submission_url": self.submission_url,
            "deadline": str(self.deadline),
            "created_at": str(self.created_at),
            "evaluation_result": self.evaluation_result
        }
    
    @gl.public.view
    def get_status(self) -> str:
        """Quick status check."""
        return self.status
    
    @gl.public.view
    def get_evaluation(self) -> str:
        """Returns the AI evaluation result (if evaluated)."""
        return self.evaluation_result
    
    @gl.public.view
    def is_deadline_passed(self) -> bool:
        """Check if the deadline has passed."""
        return gl.block.timestamp > self.deadline
    
    @gl.public.view
    def time_remaining(self) -> u256:
        """Seconds until deadline (0 if passed)."""
        if gl.block.timestamp >= self.deadline:
            return 0
        return self.deadline - gl.block.timestamp
