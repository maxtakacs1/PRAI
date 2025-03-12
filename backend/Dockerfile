FROM python:3.12-slim

# Install Poetry
RUN pip install poetry==1.6.1

# Configure Poetry to install dependencies globally
RUN poetry config virtualenvs.create false

# Set the working directory
WORKDIR /code

# Copy project metadata
COPY ./pyproject.toml ./README.md ./poetry.lock* ./

# Copy package files (if applicable)
COPY ./package[s] ./packages

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application source code
COPY ./app ./app

# Copy the .env file
COPY .env .env

# Reinstall app dependencies in case of updates
RUN poetry install --no-interaction --no-ansi

# Expose the application's port
EXPOSE 8080

# Start the application
CMD exec uvicorn app.server:app --host 0.0.0.0 --port 8080