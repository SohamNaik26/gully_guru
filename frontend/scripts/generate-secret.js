#!/usr/bin/env node

/**
 * This script generates a secure random string that can be used as NEXTAUTH_SECRET
 * Run this script with: node scripts/generate-secret.js
 */

const crypto = require("crypto");

// Generate a random string of the specified length
function generateRandomString(length = 32) {
  return crypto.randomBytes(length).toString("hex");
}

const secret = generateRandomString();

console.log("\n=== NextAuth Secret Generator ===");
console.log("\nGenerated NEXTAUTH_SECRET:");
console.log(`\n${secret}`);
console.log("\nAdd this to your .env.local file:");
console.log(`\nNEXTAUTH_SECRET=${secret}\n`);
console.log(
  "Make sure to restart your Next.js server after updating the environment variables.\n"
);
