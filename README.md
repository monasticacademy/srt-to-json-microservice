# SRT Parser API

## Overview
The SRT Parser API is a web service that accepts SubRip Text (SRT) format data and returns the parsed content in JSON format. It is designed to be used by applications that need to process subtitle files and extract timing and textual data.

## API Call and Response Example

### Request:
To parse SRT content, send a POST request to `/parse_srt` with the SRT file content as plain text in the body of the request. You must include an `X-API-KEY` in the header for authentication.

Example using `curl`:
```
curl -X POST http://<cloud_run_url>/parse_srt \
     -H "X-API-KEY: YourAPIKey" \
     -H "Content-Type: text/plain" \
     --data-binary @yourfile.srt
```

### Response:
The response will be a JSON array of subtitle entries, each containing the index, content, and start/end timings in milliseconds.

Example response:
```json
[
  {
    "index": 1,
    "content": "Subtitle text here",
    "start": 1000,
    "end": 5000
  },
  ...
]
```

## API Documentation
After deploying the application, you can access the auto-generated Swagger API documentation at `/apidocs` endpoint.

## Authentication
The default authentication method is an API key sent as a header (`X-API-KEY`). The key must match the one set in the environment variable `API_KEY`.

## Logging
The application uses Python's logging module to log information to standard error (stderr). After each request, it logs the IP address, the request method, URL scheme, path, and the response status. Logging helps monitor the application's usage and troubleshoot issues.

## Installation on Cloud Run and Continuous Deployment with Cloud Build

### Setup on Google Cloud Run:
1. Create a new project on Google Cloud Platform (GCP).
2. Enable the Cloud Run and Cloud Build APIs for your project.
3. Install and initialize the Google Cloud SDK on your local machine.
4. Authenticate with GCP: `gcloud auth login`
5. Submit a build to Cloud Build and deploy to Cloud Run:
```
gcloud builds submit --tag gcr.io/your-project-id/your-app-name
gcloud run deploy --image gcr.io/your-project-id/your-app-name --platform managed
```

### Continuous Deployment from GitHub:
1. Connect your GitHub repository to Cloud Build.
2. Set up a trigger on Cloud Build to automatically build and deploy your application to Cloud Run whenever changes are pushed to your repository.

## Non-Technical Explanation

### What is SRT?
SRT (SubRip Subtitle) is a file format used to store subtitles for video content. It contains the sequence of subtitles with their corresponding start and end times, allowing video players to display subtitles in sync with the video.

### API Call Parameters:
- `X-API-KEY`: A secret key that verifies the user is authorized to use the API.
- SRT Content: The actual subtitle text that you want to convert to JSON.

### Understanding the Response:
- `index`: A number that represents the order of the subtitle in the video.
- `content`: The text of the subtitle that should appear on the screen.
- `start`: The time (in milliseconds) when the subtitle should appear.
- `end`: The time (in milliseconds) when the subtitle should disappear.

The API takes the SRT content, reads through it, and breaks it down into a list where each item is a chunk of text with its timing information. This allows other applications to use subtitle data in various ways, such as displaying them on different media players or analyzing the text for further processing.

For more details and updates, please visit our GitHub repository or contact our support team.