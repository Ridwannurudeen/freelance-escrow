import { createClient, createAccount, generatePrivateKey } from "genlayer-js";
import { simulator } from "genlayer-js/chains";
import { readFileSync, writeFileSync } from "fs";
import path from "path";

const STUDIO_RPC = "https://studio.genlayer.com/api";

async function main() {
  console.log("Creating a fresh account for deployment...");
  const privateKey = generatePrivateKey();
  const account = createAccount(privateKey);
  console.log(`Account address: ${account.address}`);
  console.log(`Private key: ${privateKey}`);

  writeFileSync("deploy-account.json", JSON.stringify({
    address: account.address,
    privateKey: privateKey,
  }, null, 2));
  console.log("Account saved to deploy-account.json\n");

  // Use the simulator chain definition but point to the online Studio
  const client = createClient({
    chain: simulator,
    account,
    endpoint: STUDIO_RPC,
  });

  const contractPath = path.resolve("contracts/freelance_escrow.py");
  const contractCode = new Uint8Array(readFileSync(contractPath));
  console.log(`Contract loaded: ${contractPath} (${contractCode.length} bytes)`);

  console.log("\nInitializing consensus smart contract...");
  await client.initializeConsensusSmartContract();
  console.log("Consensus contract initialized.");

  console.log("\nDeploying FreelanceEscrow contract...");
  console.log('Args: "Build a Landing Page", requirements, 72 hours\n');

  const deployHash = await client.deployContract({
    code: contractCode,
    args: [
      "Build a Landing Page",
      "Create a responsive landing page with hero section, features grid, testimonials, and contact form. Must be mobile-friendly and load under 3 seconds.",
      72
    ],
    value: BigInt(1000000),
  });

  console.log(`Deploy tx hash: ${deployHash}`);
  console.log("Waiting for transaction receipt (this may take a minute)...\n");

  const receipt = await client.waitForTransactionReceipt({
    hash: deployHash,
    status: "ACCEPTED",
    interval: 5000,
    retries: 60,
  });

  console.log("Receipt:", JSON.stringify(receipt, null, 2));

  const contractAddress = receipt?.data?.contract_address;
  if (contractAddress) {
    console.log(`\n=============================`);
    console.log(`CONTRACT DEPLOYED`);
    console.log(`Address: ${contractAddress}`);
    console.log(`Tx Hash: ${deployHash}`);
    console.log(`=============================\n`);

    writeFileSync("app/.env", `VITE_CONTRACT_ADDRESS=${contractAddress}\nVITE_STUDIO_URL=${STUDIO_RPC}\n`);
    console.log("app/.env updated automatically!");
  }
}

main().catch(err => {
  console.error("Deployment failed:", err.message || err);
  process.exit(1);
});
