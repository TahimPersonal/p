# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the health check port
EXPOSE 8080

# Start the bot and health check
CMD ["python", "bot.py"]
