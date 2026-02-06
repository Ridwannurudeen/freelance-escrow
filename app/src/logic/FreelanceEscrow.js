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
    const details = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_job_details",
      args: [],
    });
    return details;
  }

  async getStatus() {
    const status = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_status",
      args: [],
    });
    return status;
  }

  async getEvaluation() {
    const evaluation = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_evaluation",
      args: [],
    });
    return evaluation;
  }

  async isDeadlinePassed() {
    const passed = await this.client.readContract({
      address: this.contractAddress,
      functionName: "is_deadline_passed",
      args: [],
    });
    return passed;
  }

  async getTimeRemaining() {
    const remaining = await this.client.readContract({
      address: this.contractAddress,
      functionName: "time_remaining",
      args: [],
    });
    return remaining;
  }

  async acceptJob() {
    const txHash = await this.client.writeContract({
      address: this.contractAddress,
      functionName: "accept_job",
      args: [],
    });
    const receipt = await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: "FINALIZED",
      interval: 10000,
    });
    return receipt;
  }

  async submitWork(url) {
    const txHash = await this.client.writeContract({
      address: this.contractAddress,
      functionName: "submit_work",
      args: [url],
    });
    const receipt = await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: "FINALIZED",
      interval: 10000,
    });
    return receipt;
  }

  async evaluateAndRelease() {
    const txHash = await this.client.writeContract({
      address: this.contractAddress,
      functionName: "evaluate_and_release",
      args: [],
    });
    const receipt = await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: "FINALIZED",
      interval: 10000,
      retries: 30,
    });
    return receipt;
  }

  async cancelJob() {
    const txHash = await this.client.writeContract({
      address: this.contractAddress,
      functionName: "cancel_job",
      args: [],
    });
    const receipt = await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: "FINALIZED",
      interval: 10000,
    });
    return receipt;
  }

  async claimDeadlineRefund() {
    const txHash = await this.client.writeContract({
      address: this.contractAddress,
      functionName: "claim_deadline_refund",
      args: [],
    });
    const receipt = await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: "FINALIZED",
      interval: 10000,
    });
    return receipt;
  }

  async withdrawAsFreelancer() {
    const txHash = await this.client.writeContract({
      address: this.contractAddress,
      functionName: "withdraw_as_freelancer",
      args: [],
    });
    const receipt = await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: "FINALIZED",
      interval: 10000,
    });
    return receipt;
  }
}

export default FreelanceEscrow;
