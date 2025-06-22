const noblox = require("noblox.js");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const axios = require("axios");
const chalk = require("chalk");

console.log(chalk.yellow("> Created by breadbars on youtube"));

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function question(query) {
    return new Promise(resolve => rl.question(query, resolve));
}

(async () => {
    const assetId = await question(chalk.blue("[+] Enter Model ID: "));
    const useCookiesFile = (await question(chalk.blue("[+] Use cookies.txt? (yes/no): "))).trim().toLowerCase();

    let cookies = [];

    const cookiesFilePath = path.join(__dirname, "cookies.txt");

    if (useCookiesFile === "yes") {
        if (!fs.existsSync(cookiesFilePath)) {
            console.log(chalk.red(`${cookiesFilePath} not found!`));
            rl.close();
            return;
        }
        cookies = fs.readFileSync(cookiesFilePath, "utf-8").split(/\r?\n/).filter(Boolean);
    } else {
        const manualCookie = await question(chalk.blue("[+] Enter Roblox Cookie: "));
        if (!manualCookie) {
            console.log(chalk.red("No cookie provided!"));
            rl.close();
            return;
        }
        cookies = [manualCookie.trim()];
    }

    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i];
        console.log(`\n----------\nProcessing cookie ${i + 1}...`);

        try {
            await noblox.setCookie(cookie);
            const currentUser = await noblox.getCurrentUser();
            const userId = currentUser.UserID;
            const username = currentUser.UserName;
            console.log(chalk.green(`[+] Logged in as ${username} (${userId})`));

            // Purchase asset - there's no noblox function, using axios with CSRF token
            const axiosInstance = axios.create({
                headers: {
                    "Cookie": `.ROBLOSECURITY=${cookie}`,
                    "User-Agent": "Roblox/WinInet",
                },
                withCredentials: true
            });

            // Get CSRF Token
            let csrfRes = await axiosInstance.post("https://auth.roblox.com/v2/logout").catch(e => e.response);
            let csrfToken = csrfRes?.headers?.["x-csrf-token"];
            if (!csrfToken) {
                console.log(chalk.red("[-] Failed to fetch X-CSRF-TOKEN."));
                continue;
            }
            axiosInstance.defaults.headers.common["X-CSRF-TOKEN"] = csrfToken;
            axiosInstance.defaults.headers["Content-Type"] = "application/json";

            // Purchase Asset
            const purchaseData = {
                expectedPrice: {
                    currencyCode: "USD",
                    quantity: {
                        significand: 0,
                        exponent: 0
                    }
                },
                productKey: {
                    productNamespace: "PRODUCT_NAMESPACE_CREATOR_MARKETPLACE_ASSET",
                    productType: "PRODUCT_TYPE_MODEL",
                    productTargetId: assetId
                }
            };

            let purchaseRes = await axiosInstance.post("https://apis.roproxy.com/marketplace-fiat-service/v1/product/purchase", purchaseData);
            if (purchaseRes.status === 200) {
                console.log(chalk.green(`[+] ${username} | Purchase Success. | ${purchaseRes.status}`));
            } else {
                console.log(chalk.red(`[-] ${purchaseRes.status} | Purchase failed.`));
                console.log(purchaseRes.data);
                continue;
            }

            // Vote (like)
            let voteRes = await axiosInstance.post(`https://apis.roproxy.com/voting-api/vote/asset/${assetId}?vote=true`);
            if (voteRes.status === 200) {
                console.log(chalk.green(`[+] ${username} | Voting Success. | ${voteRes.status}`));
            } else {
                console.log(chalk.red(`[-] ${voteRes.status} | Voting failed.`));
                console.log(voteRes.data);
            }

        } catch (err) {
            console.log(chalk.red("An error occurred:"));
            console.log(chalk.yellow(err.stack || err.message));
        }
    }

    console.log("----------\nFinished processing all cookies.");
    rl.question(chalk.cyan("\nPress Enter to exit..."), () => rl.close());
})();
