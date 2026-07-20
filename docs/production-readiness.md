# Production Readiness Checklist

## Security

Production applications must follow strict security rules to keep data safe. All private routes need standard token authentication so unauthorized users cannot access them. Rate limits are necessary to stop spam and keep the server running smoothly. Finally, system errors must be caught safely inside the code so secret details or error logs are never shown to users.

## Reliability

The application must handle problems automatically without crashing. When external services fail, the system should retry automatically after a short wait. Clear limits, like maximum message lengths and step counts, stop infinite loops and lower operating costs. If something fails, the app must handle it quietly and keep running.

## Data Consistency

Data saving must work correctly even if the application restarts. Chat history needs to be linked to specific user accounts so users never see each other's messages. Database operations must save each conversation turn in order and reload the full chat history accurately whenever requested.

## Quality and Observability

All automated tests must pass quickly without needing an internet connection or live paid services. The application needs structured logging to keep track of traffic, speed, and errors in real time. Special endpoints, like `/health` and `/metrics`, must stay active to display server status and application health.

## Documentation

Documentation must be simple and up to date. The main README.md file and every document inside the docs/ folder must accurately describe how to set up the project, run the code, use the API endpoints, and understand the project files.