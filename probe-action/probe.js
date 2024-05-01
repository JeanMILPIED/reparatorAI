const puppeteer = require('puppeteer');
const TARGET_URL = "https://reparatorai.streamlit.app/";
const WAKE_UP_BUTTON_TEXT = "app back up";
const PAGE_LOAD_GRACE_PERIOD_MS = 8000;

console.log(process.version);

(async () => {
     const browser = await puppeteer.launch({
        headless:true,
        ignoreHTTPSErrors:true,
        args: ['--no-sandbox']
  });

    const page = await browser.newPage();
    console.log(page); // Print the page object to inspect its properties

    await page.goto(TARGET_URL);

    console.log(page); // Print the page object to inspect its properties

    // Wait a grace period for the application to load
    await page.waitForTimeout(PAGE_LOAD_GRACE_PERIOD_MS);

    const checkForHibernation = async (target) => {
        // Look for any buttons containing the target text of the reboot button
        const [button] = await target.$x(`//button[contains(., '${WAKE_UP_BUTTON_TEXT}')]`);
        if (button) {
            console.log("App hibernating. Attempting to wake up!");
            await button.click();
        }
    }

    await checkForHibernation(page);
    const frames = (await page.frames());
    for (const frame of frames) {
        await checkForHibernation(frame);
    }

    await browser.close();
})();
