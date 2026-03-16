# Marketing Agent Deployment Guide

This guide provides step-by-step instructions to set up and deploy the Marketing Agent using Vellum AI. It covers creating a Docker environment, uploading it to Vellum AI, and configuring essential environment variables.

## Prerequisites

Before proceeding, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Vellum CLI](https://docs.vellum.ai/developers/cli/installation)
- A Vellum AI account (sign up at [app.vellum.ai](https://app.vellum.ai/signup))

## Step 1: Create a Docker Environment

To containerize the Marketing Agent, follow these steps:

1. **Create a Dockerfile**: In the `marketing_agent` directory, create a file named `Dockerfile` with the following content:

    ```dockerfile
    FROM vellumai/python-workflow-runtime:latest

    # Install any additional dependencies you need
    RUN pip install --upgrade pip && pip install pymongo peopledatalabs opencv-python==4.12.0.88 praw
    RUN apt-get update && apt-get install -y \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        ffmpeg \
        tzdata \
        ca-certificates

    # Copy any custom code or utilities
    # COPY ./utils /custom/utils

    # Set environment variables if needed
    # ENV PYTHONPATH="${PYTHONPATH}:/custom"

    CMD ["vellum_start_server"]
    ```

    **Notes**:
    - The base image `vellumai/python-workflow-runtime:latest` is essential for compatibility with Vellum's infrastructure.
    - The `vellum_start_server` command initiates the Vellum server within the container.
    - Additional dependencies include MongoDB client, People Data Labs API, OpenCV, and Reddit API wrapper.

2. **Build the Docker Image**: Execute the following command in the terminal:

    ```bash
    docker build -t marketing-agent:1.0.0 .
    ```

    This command builds the Docker image and tags it as `marketing-agent` with version `1.0.0`.

## Step 2: Upload the Docker Image to Vellum AI

After building the Docker image, upload it to Vellum AI:

1. **Push the Docker Image**: Use the Vellum CLI to push the image:

    ```bash
    vellum image push marketing-agent:1.0.0 --tag latest
    ```

    This command uploads the Docker image to Vellum AI and tags it as `latest`.

2. **Configure the Workflow to Use the Custom Image**: In your project's `pyproject.toml` file, add the following configuration:

    ```toml
    [[tool.vellum.workflows]]
    module = "marketing_agent"
    container_image_name = "marketing-agent"
    container_image_tag = "1.0.0"
    ```

    This configuration instructs Vellum to use the specified Docker image when running the `marketing_agent` workflow.

## Step 3: Configure Environment Variables in Vellum AI

Environment variables allow you to manage configuration settings that may vary between different environments (e.g., development, staging, production). To set up environment variables in Vellum AI:

1. **Navigate to Workspace Settings**: In the Vellum AI interface, go to the **Workspace Settings**.

2. **Access the Environment Variables Tab**: Click on the **Environment Variables** tab.

3. **Add the Required Environment Variables**:

### Required Environment Variables

| Variable Name | Description | Example Value | Required |
|---------------|-------------|---------------|----------|
| `MONGODB_URI` | MongoDB connection string for storing product marketing data | `mongodb+srv://username:password@cluster.mongodb.net/marketing_db` | Yes |
| `PDL_API_KEY` | People Data Labs API key for email extraction | `pdl_api_key_here` | No (fallback emails provided) |
| `CAPTIONS_API_KEY` | Captions.ai API key for video generation | `captions_api_key_here` | No (for LinkedIn video posts) |

### Optional Environment Variables

| Variable Name | Description | Example Value | Required |
|---------------|-------------|---------------|----------|
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn API access token for posting | `linkedin_token_here` | No (hardcoded in code) |
| `GMAIL_APP_PASSWORD` | Gmail app password for email sending | `gmail_app_password_here` | No (hardcoded in code) |

### Environment Variable Configuration Steps

1. **Click on "Add Environment Variable"**
2. **Enter the variable name in `CAPITALIZED_SNAKE_CASE` format** (e.g., `MONGODB_URI`)
3. **Assign values for each environment** (development, staging, production)
4. **For sensitive information like API keys**, use secret references instead of plain text values
5. **Set the appropriate scope** (workflow-specific or workspace-wide)

### Example .env Structure (for local development)

```bash
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/marketing_db

# API Keys
PDL_API_KEY=your_people_data_labs_api_key_here
CAPTIONS_API_KEY=your_captions_ai_api_key_here

# LinkedIn Configuration (optional - can be hardcoded)
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token_here

# Email Configuration (optional - can be hardcoded)
GMAIL_APP_PASSWORD=your_gmail_app_password_here
```

## Step 4: Deploy and Test

1. **Deploy the Workflow**: Use the Vellum CLI to deploy your workflow:

    ```bash
    vellum workflow deploy marketing_agent
    ```

2. **Test the Deployment**: In the Vellum AI interface, navigate to your deployed workflow and test it with sample inputs.

## Step 5: Monitor and Debug

1. **View Logs**: Monitor execution logs in the Vellum AI interface
2. **Check Metrics**: Review performance metrics and error rates
3. **Debug Issues**: Use the built-in debugging tools to troubleshoot any problems

## Additional Resources

- [Vellum AI Documentation](https://docs.vellum.ai/)
- [Vellum CLI Installation Guide](https://docs.vellum.ai/developers/cli/installation)
- [Docker Installation Guide](https://docs.docker.com/get-docker/)
- [MongoDB Atlas Setup](https://docs.atlas.mongodb.com/getting-started/)
- [People Data Labs API Documentation](https://docs.peopledatalabs.com/)

## Troubleshooting

### Common Issues

1. **Docker Build Failures**: Ensure all dependencies are compatible with the base image
2. **Environment Variable Issues**: Verify variable names match exactly (case-sensitive)
3. **MongoDB Connection Errors**: Check network access and authentication credentials
4. **API Key Validation**: Ensure API keys are valid and have proper permissions

### Getting Help

- Check the [Vellum AI Support Documentation](https://docs.vellum.ai/home/getting-started/support)
- Join the [Vellum Community Discord](https://discord.gg/vellum-ai)
- Contact Vellum AI support through the platform

By following this guide, you can successfully set up and deploy the Marketing Agent using Vellum AI, ensuring a consistent and configurable environment across different stages of development and production.
