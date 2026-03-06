# PRIMO - The P&A Project Optimizer Application

<summary>Table of Contents</summary>
    <ol>
        <li>
            <a href='#about-the-project'>About the Project</a>
            <ul>
                <li><a href="#built-with">Built With</a></li>
            </ul>
        </li>
        <li>
            <a href="#getting-started">Getting Started</a>
            <ul>
                <li><a href="#laravel-setup">Laravel Setup</a></li>
                <li><a href="#redis">Redis</a></li>
                <li><a href="#configuring-mapbox">Configuring Mapbox</a></li>
            </ul>
        </li>
        <li>
            <a href="#development-conventions">Development Conventions</a>
            <ul>
                <li>
                    <a href="#husky-use-and-setup">Husky Setup</a>
                </li>
            </ul>
        </li>
        <li>
            <a href="#creating-pull-requests">Creating Pull Requests</a>
        </li>
        <li>
            <a href="#branching-strategy">Branching strategy</a>
        </li>
        <li>
            <a href="#versioning-and-changelog-generation">Versioning and Changelog Generation</a>
        </li>
         <li>
            <a href="#github-actions">Github Actions</a>
        </li>
        <li>
            <a href="#recommended-development-tools">Recommended Development Tools</a>
        </li>
    </ol>

## About The Project

This project serves as a web interface for the [PRIMO API](https://github.com/NEMRI-org/primo-ui-web-api) project.

### Built With

[![Vue][Vue.js]][Vue-url] [![Laravel][Laravel.com]][Laravel-url]

## Getting Started

1. Clone the repo:
    ```
    git clone git@github.com:Troy-Web-Consulting/netl-mwu.git
    ```
2. Install the dependencies:
    ```
    npm install
    ```
3. Install the dependencies in each subdirectory:
    ```
    cd frontend
    npm install
    ```
    ```
    cd api
    npm install
    ```
4. Start the frontend:
    ```
    cd frontend
    npm run dev
    ```
5. Start the backend:
    ```
    cd api
    npm run dev
    ```

### Laravel Setup

1. Install [Larave Herd](https://herd.laravel.com/docs/1/getting-started/installation) using PHP 8.2.
2. Point Herd's 'sites' configuration to the cloned directory.
3. (Optional) With Herd Pro, create a Redis queue, MySQL DB and MongoDB DB.
4. Install the Laravel dependencies:
    ```
    composer install
    ```
5. Create an `.env` file in the api directory and add the necessary environment variables:
    ```
    cd api
    cp .env.example .env
    ```
6. Generate a new application key:
    ```
    php artisan key:generate
    ```
7. Run the migrations:
    ```
    php artisan migrate
    ```

### Redis

Some functionality of the application requires Redis. To use Redis with Laravel Herd, follow the instructions below:

1. Open the Herd dashboard and navigate to services.
2. Add a **redis** service on a port that doesn't conflict with another service port.
3. Update the `QUEUE_CONNECTION` and `REDIS_PORT` variables in the _.env_ file.

### Configuring Mapbox

In order to view the maps in the frontend application, you will need to have a Mapbox account and a Mapbox access token. The following steps will guide you through the process of setting up the frontend application to use Mapbox.

1. Create a Mapbox account by visiting the [Mapbox website](https://account.mapbox.com/auth/signup/). This can be a personal account.
2. After following the steps to create an account, navigate to the [Mapbox tokens page](https://account.mapbox.com/access-tokens/).
3. In the root of the `frontend/` directory, create a file named `.env`.
4. In the `.env` file, add the following line:
    ```bash
    VITE_APP_MAPBOX_TOKEN=YOUR_PUBLIC_TOKEN_FROM_MAPBOX
    ```

You're all set! The frontend application should now be able to display maps.

## Development Conventions

This project utilizies [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) as the guiding principle for commit messages. This allows for automatic versioning and changelog generation.

Reference [this article](https://medium.com/neudesic-innovation/conventional-commits-a-better-way-78d6785c2e08) for the commit linting strategy used for this project.

Some guiding principles for commit messages are as follows:

1. Use the present tense ("fix bug to mapping" : "add feature to enable toggling of...")
2. Use lowercase for the initial message.
3. Use sentence case (first word capitalized) for the body of the message.

### Husky use and setup

To enable pre-commit linting and formatting, add the correct path to your NPM version.

For example try this:

(If you do not already have a husky init file):

```
cd
cd ~/.config
mkdir husky (if it does not exist)
touch init.sh (if it does not exist)
```

Then open the file in nano:

```
cd
nano ~/.config/husky/init.sh
```

In the file paste the following:

```
PATH="/usr/local/bin:$PATH"
```

Alternativelty, if you are using NVM you can add the following:

```
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

In order to run pint, it is very likely you will have to add your php path to the husky init.sh file. You can find this by running `which php` in your terminal. Then add the line to the init.sh file.

For example:

```
export PATH="/Users/my-user/Library/Application Support/Herd/bin:$PATH"
```

This may require resetting your IDE before it will take affect. Further troubleshooting instructions can be found [here](https://typicode.github.io/husky/troubleshoot.html).

Reference [this article](https://medium.com/neudesic-innovation/conventional-commits-a-better-way-78d6785c2e08) for the commit linting strategy used here.

## Creating Pull Requests

When creating a pull request, please follow these guidelines:

1. Copy the Issue title, including the number and paste it (prepended with a valid convential commit type) as the PR title. This will result in a github action auto-filling the PR labels and milestone.

```
ex. docs: README - Update Versions Documentation #392
```

2. In the 'Development' section of the PR, search the issue number relating to the PR and link them.
3. Wait for all checks to pass before notifying your reviewer that you are ready for a code review.

## Branching Strategy

The branching strategy used for this project is as follows:

1. `main` &rarr; Stable production-ready code.
2. `develop` &rarr; Active development for upcoming releases.
3. `feature/*` &rarr; For new features.
4. `bugfix/*` &rarr; For bug fixes.
5. `hotfix/*` &rarr; For urgent fixes to production.
6. `release/*` &rarr; (Optional) For preparing a new releases (if needed).

**Feature** branches should be created off of the `develop` branch and merged back into the `develop` branch when the feature is complete. The branches should be prepended with the type of work being done followed by the ticket number (e.g. `feature/202`, `bugfix/115`) .

**Hotfix** branches should be created off of the `main` branch and merged back into the `main` branch when the hotfix is complete. These branches follow a similar convention (e.g. `hotfix/202`).

### Important:

**Feature merges into the develop branch should use the "Squash and Merge" method.**

## Releases, Versioning and Changelog Generation (WIP)

### Initial Setup:

Install the changelog package globally if you have not already: `npm install -g conventional-changelog-cli`.

### Pre-release verisioning (QA/UAT):

Pre-releases are used to track changes that are not yet ready for production. To create a pre-release, follow these steps:

1. Once a change or a set of changes has been merged into the `develop` branch, pull the most recent version of the `develop` branch locally.
2. Run the `npm version` command, specifying the type of version bump you want to make. For example, to bump the version to a new minor version, run `npm version minor` or for prerelease versions `npm version prerelease -preid=alpha`. Typically this will be a prerelease version.

    a. _Optional:_ use _-beta.X_ once stable, or _-rc.x_ for final testing before release. An example of this flow is:

    ```
    ex. v0.1.1-alpha.1 -> v0.1.1-beta.1 -> v0.1.1-rc.1 -> v0.1.1 (Production)
    ```

3. The result should be a new `release/` branch, with an updated version number, a new CHANGELOG.md entry and git tag pushed to Github.
4. Create a PR, and merge (DO NOT squash and merge) the `release/` branch into the `develop` branch. Title the PR something like `chore(release): v1.2.3`.
5. Create a new [Github Release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release) using the newly created tag, **important:** mark this with 'Set as a pre-release'. Click "Generate release notes", then publish the release.
6. For testing, pull the branch and tags into the QA environment, and use `git checkout vTAGNAME` to test the release.

### Handling Hotfixes:

Hotfixes are handled in much the same way as features, however, these fixes originate on the `main` branch.

1. Create a new branch off of the `main` branch, with the name `hotfix/` followed by the ticket number (e.g. `hotfix/202`).
2. Make the necessary changes, and then create a PR to merge the hotfix branch back into the `main` branch.
3. Once the PR is merged, pull the `main` branch, and run `npm version` to bump the version number (typically this should increment the patch version).
4. Deploy the changes to the QA/UAT environment (making sure to coordinate and also deploy the proper python codebase version is necessary) for validation.
5. Once validated, merge the `main` branch back into the `develop` branch, and create a new release on Github, using the tag that was created by the `npm version` command, and the CHANGELOG.md entry for that tag.  
   a. All subsequent changes to the `develop` branch should begin as a new version, for example:

```
ex. hotfix/202 -> main -> v0.1.1, future development is v0.1.2-alpha.1
```

Then follow these steps (which can be modified for hotfixes):

1. Pull the most recent version of the `develop` branch locally, which should contain the changes your are ready to deploy to production.
2. Run the `npm version` command, specifying the type of version bump you want to make. For example, to bump the version to a new minor version, run `npm version minor` or for prerelease versions `npm version prerelease -preid=alpha`.
3. The result should be a new `release/` branch, with an updated version number, a new CHANGELOG.md entry and git tag pushed to Github.
4. Create a PR, and merge (DO NOT squash and merge) the `release/` branch into the `main` branch. Title the PR something like `chore(release): v1.2.3`.
5. Once the PR is merged, create a new release on Github, using the tag that was created by the `npm version` command, and the CHANGELOG.md entry for that tag.
6. Once the release is created, merge the `main` branch back into the `develop` branch.

### Semvar

Following the release of the first production version, the project will follow the [Semantic Versioning](https://semver.org/) standard.

## Github Actions

### Commitlint Check

The "Commitlint Check" action triggers on Pull Requests, and is aimed to enforce the use of convention commits. If the PR fails, view the detailed output provided by the action. [This is a good guide](https://devmount.medium.com/how-to-correct-git-commit-messages-334bd35541e) on how to update old commit messages.

For older messages you can implement the following steps:

1. Identify the hash of the bad commit(s) using `git log` and the commit message output from the aciton.
2. Run `git rebase -i HASH^`.
3. Type `i` to enter insert mode.
4. Replace `pick` with `reword` for the bad commit.
5. Save and exit the editor using `Esc` and `:wq`.
6. In the git prompt enter insert mode again `i`.
7. Update the commit message (top line) as per the commitlint rules.
8. Save and exit the editor using `Esc` and `:wq`.
9. Repeat for all bad commits.
10. Run `git push --force`.

## Recommended Development Tools

The following are a list of recommended, albeit optional, development tools that can be used to enhance the development experience:

1. [TablePlus](https://tableplus.com/) manage multiple databases with easy to use UI.
2. [MongoDB Compass](https://www.mongodb.com/products/compass) a GUI for MongoDB.
3. [Conventional Commits (VSCode Extension)](https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits) a VSCode extension that makes it easier to follow the Conventional Commits standard.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
