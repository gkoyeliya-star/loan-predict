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
-   **Build Command**: `pip install -r requirements.txt`
-   **Start Command**: `gunicorn wsgi:app`
-   **Instance Type**: `Free`

### Step 3: Add Environment Variables

Before deploying, you need to tell Render which Python version to use.

1.  Scroll down to the **"Advanced"** section and click it to expand.
2.  Click **"+ Add Environment Variable"**.
3.  Create the following variables:
    -   **Key**: `PYTHON_VERSION`
        **Value**: `3.11.0`
    -   **Key**: `SECRET_KEY`
        **Value**: *(generate a long random secret)*
    -   **Key**: `FLASK_ENV`
        **Value**: `production`

### Step 4: Deploy!

1.  Scroll to the bottom of the page and click the **"Create Web Service"** button.
2.  Render will now pull your code from GitHub, install dependencies from `requirements.txt`, and then start the application using the Gunicorn start command.
3.  You can watch the deployment progress in the "Events" and "Logs" tabs.

**That's it!** Once the deployment is complete, Render will provide you with a public URL (e.g., `https://loan-easy.onrender.com`) where your application will be live.

### Why These Settings?

-   **`pip install -r requirements.txt`**: Installs all Python packages needed by the app.
-   **`gunicorn wsgi:app`**: Runs your application via Gunicorn, a production-grade server.
-   **`PYTHON_VERSION`**: This ensures Render uses the same version of Python you used for development, preventing compatibility issues.
-   **`PORT`**: Render assigns a port dynamically. If you customize the Gunicorn command, bind to `$PORT`.
