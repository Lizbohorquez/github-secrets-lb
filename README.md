# Github Secrets

GitHub Repository Secrets Comparator

## Description

This project aims to compare secrets across multiple GitHub repositories. It provides a convenient way to retrieve and compare secrets stored in the repositories, helping identify potential security risks and ensure consistent secret management practices.

## Features

- Retrieve secrets from GitHub repositories
- Compare secrets across multiple repositories
- Highlight differences and similarities in secret values
- Support for repositories within an organization or individual user repositories
- Customizable filtering options (e.g., by repository name, secret name)
- Secure authentication using GitHub personal access token

## Installation

1. Clone the repository to your local machine:
   ```
   git clone https://github.com/HolisticDevelop/github-secrets.git
   ```

2. Install the project dependencies using pip:
   ```
   pip install -r requirements.txt
   ```

3. Obtain a personal access token from GitHub:
   - Go to your GitHub account settings.
   - Navigate to "Developer settings" > "Personal access tokens".
   - Generate a new token with the appropriate permissions to access the repositories and secrets you want to compare.

4. Create a `.env` file in the project root directory and add the following environment variables:
   ```
   GITHUB_TOKEN=<your-personal-access-token>
   BRANCH=<random-branch-name>
   USERNAME=<github-username>
   ORG=<optional-if-into-a-org>
   ```

## Usage

1. Open a terminal or command prompt and navigate to the project directory.

2. Run the script to compare secrets:
   ```
   python app.py
   ```

3. Follow the prompts to provide the necessary inputs:
   - Select the repositories to compare (individual repositories or organization repositories).
   - Specify any filtering options if desired (e.g., repository name, secret name).
   - The script will retrieve and compare the secrets, displaying the results on the console.


Need Approve --> f1
Not Need Approve -->f2