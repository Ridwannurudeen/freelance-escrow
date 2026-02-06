<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-4xl mx-auto py-6 px-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Freelance Escrow</h1>
        <div>
          <div v-if="!userAddress">
            <button
              @click="createUserAccount"
              class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg text-sm"
            >
              Connect Wallet
            </button>
          </div>
          <div v-else class="flex items-center gap-4">
            <span class="text-sm text-gray-500">
              <Address :address="userAddress" />
            </span>
            <button
              @click="disconnectUserAccount"
              class="text-sm text-gray-400 hover:text-gray-600"
            >
              Disconnect
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto py-8 px-4">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="text-gray-400">Loading contract data...</div>
      </div>

      <!-- Job Card -->
      <div v-else class="space-y-6">
        <!-- Status Banner -->
        <div
          :class="statusBannerClass"
          class="rounded-lg p-4 text-center font-medium text-lg"
        >
          {{ statusLabel }}
        </div>

        <!-- Job Details -->
        <div class="bg-white rounded-lg shadow p-6 space-y-4">
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
            <div>
              <span class="text-gray-500">Client</span>
              <p class="font-mono text-xs truncate">{{ jobDetails.client || "—" }}</p>
            </div>
            <div>
              <span class="text-gray-500">Freelancer</span>
              <p class="font-mono text-xs truncate">{{ jobDetails.freelancer || "None" }}</p>
            </div>
          </div>

          <div>
            <span class="text-gray-500 text-sm">Requirements</span>
            <p class="mt-1 text-gray-700 bg-gray-50 rounded p-3 text-sm">
              {{ jobDetails.requirements || "—" }}
            </p>
          </div>

          <div v-if="jobDetails.submission_url">
            <span class="text-gray-500 text-sm">Submission URL</span>
            <p class="mt-1">
              <a
                :href="jobDetails.submission_url"
                target="_blank"
                class="text-indigo-600 hover:text-indigo-800 text-sm underline"
              >
                {{ jobDetails.submission_url }}
              </a>
            </p>
          </div>

          <div v-if="timeRemaining > 0" class="text-sm text-gray-500">
            Time remaining: {{ formatTime(timeRemaining) }}
          </div>
          <div v-else-if="deadlinePassed" class="text-sm text-red-500">
            Deadline has passed
          </div>
        </div>

        <!-- Actions -->
        <div class="bg-white rounded-lg shadow p-6" v-if="userAddress">
          <h3 class="text-lg font-medium mb-4">Actions</h3>

          <div class="space-y-3">
            <!-- Accept Job (for freelancers, when open) -->
            <button
              v-if="jobDetails.status === 'open' && userAddress !== jobDetails.client"
              @click="handleAcceptJob"
              :disabled="actionLoading"
              class="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white font-medium py-3 px-4 rounded-lg"
            >
              {{ actionLoading ? "Processing..." : "Accept Job" }}
            </button>

            <!-- Submit Work (for assigned freelancer, when in_progress) -->
            <div v-if="jobDetails.status === 'in_progress' && userAddress === jobDetails.freelancer">
              <input
                v-model="submissionUrl"
                type="url"
                placeholder="Enter deliverable URL (GitHub repo, hosted app, etc.)"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg mb-2 text-sm"
              />
              <button
                @click="handleSubmitWork"
                :disabled="actionLoading || !submissionUrl"
                class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-medium py-3 px-4 rounded-lg"
              >
                {{ actionLoading ? "Submitting..." : "Submit Work" }}
              </button>
            </div>

            <!-- Evaluate (when submitted) -->
            <button
              v-if="jobDetails.status === 'submitted'"
              @click="handleEvaluate"
              :disabled="actionLoading"
              class="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 text-white font-medium py-3 px-4 rounded-lg"
            >
              {{ actionLoading ? "AI is evaluating..." : "Trigger AI Evaluation" }}
            </button>

            <!-- Cancel Job (client only, when open) -->
            <button
              v-if="jobDetails.status === 'open' && userAddress === jobDetails.client"
              @click="handleCancelJob"
              :disabled="actionLoading"
              class="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-300 text-white font-medium py-3 px-4 rounded-lg"
            >
              {{ actionLoading ? "Cancelling..." : "Cancel Job" }}
            </button>

            <!-- Withdraw (freelancer, when in_progress) -->
            <button
              v-if="jobDetails.status === 'in_progress' && userAddress === jobDetails.freelancer"
              @click="handleWithdraw"
              :disabled="actionLoading"
              class="w-full bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-300 text-white font-medium py-3 px-4 rounded-lg"
            >
              {{ actionLoading ? "Withdrawing..." : "Withdraw from Job" }}
            </button>

            <!-- Claim Deadline Refund (client, when deadline passed) -->
            <button
              v-if="deadlinePassed && (jobDetails.status === 'open' || jobDetails.status === 'in_progress') && userAddress === jobDetails.client"
              @click="handleClaimRefund"
              :disabled="actionLoading"
              class="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-300 text-white font-medium py-3 px-4 rounded-lg"
            >
              {{ actionLoading ? "Claiming..." : "Claim Deadline Refund" }}
            </button>
          </div>
        </div>

        <!-- Evaluation Result -->
        <div v-if="evaluation" class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-medium mb-3">AI Evaluation Result</h3>
          <pre class="bg-gray-50 rounded p-4 text-sm whitespace-pre-wrap text-gray-700">{{ evaluation }}</pre>
        </div>

        <!-- Action Feedback -->
        <div v-if="feedbackMessage" :class="feedbackClass" class="rounded-lg p-4 text-sm">
          {{ feedbackMessage }}
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { account, createAccount, removeAccount } from "../services/genlayer";
import FreelanceEscrow from "../logic/FreelanceEscrow";
import Address from "./Address.vue";

// Config
const contractAddress = import.meta.env.VITE_CONTRACT_ADDRESS;
const studioUrl = import.meta.env.VITE_STUDIO_URL;
const escrow = new FreelanceEscrow(contractAddress, account, studioUrl);

// State
const userAccount = ref(account);
const userAddress = computed(() => userAccount.value?.address);
const jobDetails = ref({});
const evaluation = ref("");
const timeRemaining = ref(0);
const deadlinePassed = ref(false);
const loading = ref(true);
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
    open: "Open — Waiting for a freelancer to accept",
    in_progress: "In Progress — Freelancer is working",
    submitted: "Submitted — Ready for AI evaluation",
    completed: "Completed — Payment released to freelancer",
    refunded: "Refunded — Payment returned to client",
  };
  return labels[jobDetails.value.status] || "Unknown Status";
});

// Helpers
function formatTime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

function showFeedback(message, type = "info") {
  feedbackMessage.value = message;
  feedbackType.value = type;
  setTimeout(() => { feedbackMessage.value = ""; }, 5000);
}

// Data Loading
async function loadAll() {
  try {
    const [details, evalResult, remaining, passed] = await Promise.all([
      escrow.getJobDetails(),
      escrow.getEvaluation(),
      escrow.getTimeRemaining(),
      escrow.isDeadlinePassed(),
    ]);

    // Handle Map or plain object response
    if (details instanceof Map) {
      jobDetails.value = Object.fromEntries(details);
    } else {
      jobDetails.value = details;
    }

    evaluation.value = evalResult || "";
    timeRemaining.value = Number(remaining) || 0;
    deadlinePassed.value = !!passed;
  } catch (e) {
    console.error("Failed to load contract data:", e);
  }
}

// Account
function createUserAccount() {
  userAccount.value = createAccount();
  escrow.updateAccount(userAccount.value);
}

function disconnectUserAccount() {
  userAccount.value = null;
  removeAccount();
}

// Actions
async function handleAcceptJob() {
  actionLoading.value = true;
  try {
    await escrow.acceptJob();
    showFeedback("Job accepted successfully!", "success");
    await loadAll();
  } catch (e) {
    showFeedback(`Failed to accept job: ${e.message}`, "error");
  }
  actionLoading.value = false;
}

async function handleSubmitWork() {
  actionLoading.value = true;
  try {
    await escrow.submitWork(submissionUrl.value);
    showFeedback("Work submitted successfully!", "success");
    submissionUrl.value = "";
    await loadAll();
  } catch (e) {
    showFeedback(`Failed to submit work: ${e.message}`, "error");
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
    showFeedback(`Evaluation failed: ${e.message}`, "error");
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
    showFeedback(`Failed to cancel: ${e.message}`, "error");
  }
  actionLoading.value = false;
}

async function handleWithdraw() {
  actionLoading.value = true;
  try {
    await escrow.withdrawAsFreelancer();
    showFeedback("Withdrawn from job. Job is open again.", "success");
    await loadAll();
  } catch (e) {
    showFeedback(`Failed to withdraw: ${e.message}`, "error");
  }
  actionLoading.value = false;
}

async function handleClaimRefund() {
  actionLoading.value = true;
  try {
    await escrow.claimDeadlineRefund();
    showFeedback("Deadline refund claimed.", "success");
    await loadAll();
  } catch (e) {
    showFeedback(`Failed to claim refund: ${e.message}`, "error");
  }
  actionLoading.value = false;
}

// Init
onMounted(async () => {
  await loadAll();
  loading.value = false;
});
</script>
