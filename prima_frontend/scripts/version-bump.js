const { execSync } = require('child_process');
const fs = require('fs');

// Determine the new version number
let newVersion = require('../package.json').version;

console.log(`New version: v${newVersion}`);

// Define the new release branch based on the new version
const releaseBranch = `release/v${newVersion}`;

// Create and checkout the new release branch
execSync(`git checkout -b ${releaseBranch}`);

execSync('npx conventional-changelog  -i CHANGELOG.md -s');

// Stage the package.json and package-lock.json files (or any other files changed by the version bump)
execSync('git add package.json package-lock.json CHANGELOG.md');

// Commit the changes
execSync(`git commit -m "chore(release): bump version to v${newVersion}"`);

// Generate tag
execSync(`git tag v${newVersion}`);

// Push the new release branch to the remote
execSync(`git push origin ${releaseBranch}`);

// Push the new tag to the remote
execSync(`git push origin v${newVersion}`);

console.log(`Created new release branch: ${releaseBranch}`);
