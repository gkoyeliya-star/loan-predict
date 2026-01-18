# How to Deploy Your "LOAN EASY" Application on Render

This guide will walk you through deploying your Flask application from GitHub to Render.

### Step 1: Create a New Web Service on Render

1.  Go to your [Render Dashboard](https://dashboard.render.com/).
2.  Click the **"New +"** button and select **"Web Service"**.
3.  Connect your GitHub account if you haven't already.
4.  Find your repository (`DevDebjit83/loan-easy`) and click **"Connect"**.

### Step 2: Configure the Render Service

You will now see a configuration screen. Fill it out with the following settings:

-   **Name**: `loan-easy` (or any name you prefer).
-   **Region**: Choose a region close to you (e.g., Ohio, Frankfurt).
-   **Branch**: `main`.
-   **Runtime**: Select **`Python 3`**.
-   **Build Command**: `bash build.sh`
-   **Start Command**: `gunicorn --workers 4 --bind 0.0.0.0:$PORT wsgi:application`
-   **Instance Type**: `Free`

### Step 3: Add Environment Variables

Before deploying, you need to tell Render which Python version to use.

1.  Scroll down to the **"Advanced"** section and click it to expand.
2.  Click **"+ Add Environment Variable"**.
3.  Create the following variable:
    -   **Key**: `PYTHON_VERSION`
    -   **Value**: `3.11.0`

### Step 4: Deploy!

1.  Scroll to the bottom of the page and click the **"Create Web Service"** button.
2.  Render will now pull your code from GitHub, run the `build.sh` script to install everything, and then start the application using the Gunicorn start command.
3.  You can watch the deployment progress in the "Events" and "Logs" tabs.

**That's it!** Once the deployment is complete, Render will provide you with a public URL (e.g., `https://loan-easy.onrender.com`) where your application will be live.

### Why These Settings?

-   **`build.sh`**: This script ensures that all your Python packages from `requirements.txt` are installed and that your SQLite database is created and initialized *before* the server starts.
-   **`gunicorn ...`**: This is the command that runs your application. `gunicorn` is a robust, production-grade server that can handle multiple requests at once, which is much better than Flask's built-in development server.
-   **`PYTHON_VERSION`**: This ensures Render uses the same version of Python you used for development, preventing compatibility issues.
-   **`$PORT`**: Render assigns a port dynamically. Using `$PORT` in the start command ensures Gunicorn listens on the correct port that Render exposes to the outside world.
