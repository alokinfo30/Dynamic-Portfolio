FROM python:3.11-slim

# Create a non-root user and group
RUN addgroup --system app && adduser --system --ingroup app app

# Set environment variables for the non-root user
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
ENV PATH=${APP_HOME}/.local/bin:${PATH}
ENV PYTHONPATH=${APP_HOME}

RUN mkdir -p ${APP_HOME}
WORKDIR ${APP_HOME}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
    
# Grant ownership of the app home directory to the app user
RUN chown -R app:app ${HOME}

# Copy requirements and install Python dependencies
COPY --chown=app:app requirements.txt .
USER app
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application code
COPY --chown=app:app . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.main:create_app()"]