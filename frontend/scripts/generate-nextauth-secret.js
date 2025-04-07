#!/usr/bin/env node

/**
 * This script generates a secure random string that can be used as a NEXTAUTH_SECRET
 * It will automatically update your .env.local file with the new secret
 *
 * To run:
 * node scripts/generate-nextauth-secret.js
 */

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

// Generate a secure random string (64 bytes = 128 hex chars)
function generateSecret() {
  return crypto.randomBytes(64).toString("hex");
}

// Update the .env.local file
function updateEnv(newSecret) {
  const envPath = path.join(__dirname, "..", ".env.local");

  try {
    if (fs.existsSync(envPath)) {
      let envContent = fs.readFileSync(envPath, "utf8");

      // Check if NEXTAUTH_SECRET already exists
      if (envContent.includes("NEXTAUTH_SECRET=")) {
        // Replace existing secret
        envContent = envContent.replace(
          /NEXTAUTH_SECRET=.*/,
          `NEXTAUTH_SECRET=${newSecret}`
        );
      } else {
        // Add new secret
        envContent += `\nNEXTAUTH_SECRET=${newSecret}\n`;
      }

      fs.writeFileSync(envPath, envContent);
      console.log("✅ NEXTAUTH_SECRET updated in .env.local");
    } else {
      // Create new .env.local if it doesn't exist
      fs.writeFileSync(envPath, `NEXTAUTH_SECRET=${newSecret}\n`);
      console.log("✅ Created .env.local with NEXTAUTH_SECRET");
    }

    return true;
  } catch (error) {
    console.error("❌ Error updating .env.local:", error.message);
    return false;
  }
}

// Main function
function main() {
  console.log("🔑 Generating new NEXTAUTH_SECRET...");
  const newSecret = generateSecret();

  if (updateEnv(newSecret)) {
    console.log("\n📋 Next steps:");
    console.log("1. Restart your Next.js development server");
    console.log("2. Clear your browser cookies for this site");
    console.log("3. Try signing in again\n");
  }
}

// Run the script
main();
