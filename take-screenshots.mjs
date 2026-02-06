import puppeteer from "puppeteer";
import path from "path";

async function main() {
  const screenshotsDir = path.resolve("screenshots");

  const browser = await puppeteer.launch({
    headless: "new",
    executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"],
  });

  // Screenshot 1: The Frontend dApp
  console.log("Capturing frontend dApp...");
  const page1 = await browser.newPage();
  await page1.setViewport({ width: 1280, height: 900 });
  await page1.goto("http://localhost:5173", { waitUntil: "networkidle2", timeout: 15000 });
  await page1.waitForSelector("header", { timeout: 10000 }).catch(() => {});
  await new Promise(r => setTimeout(r, 2000)); // let Vue render
  await page1.screenshot({ path: path.join(screenshotsDir, "frontend-dapp.png"), fullPage: true });
  console.log("  -> frontend-dapp.png saved");

  // Screenshot 2: GenLayer Studio (online)
  console.log("Capturing GenLayer Studio...");
  const page2 = await browser.newPage();
  await page2.setViewport({ width: 1400, height: 900 });
  await page2.goto("https://studio.genlayer.com", { waitUntil: "networkidle2", timeout: 30000 });
  await new Promise(r => setTimeout(r, 3000));
  await page2.screenshot({ path: path.join(screenshotsDir, "genlayer-studio.png"), fullPage: false });
  console.log("  -> genlayer-studio.png saved");

  // Screenshot 3: Studio with contract transaction (explorer view)
  console.log("Capturing contract on Studio explorer...");
  const page3 = await browser.newPage();
  await page3.setViewport({ width: 1400, height: 900 });
  await page3.goto("https://studio.genlayer.com/contracts/0x7309a0390e28CCa3B284386A443508a826823c9A", {
    waitUntil: "networkidle2", timeout: 30000
  });
  await new Promise(r => setTimeout(r, 3000));
  await page3.screenshot({ path: path.join(screenshotsDir, "contract-deployed.png"), fullPage: false });
  console.log("  -> contract-deployed.png saved");

  await browser.close();
  console.log("\nAll screenshots saved to screenshots/");
}

main().catch(err => {
  console.error("Screenshot failed:", err.message);
  process.exit(1);
});
