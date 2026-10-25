# Classroom reference only: Python and libraries run inside a single container.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY security_analyst.py ./
COPY fixtures/ ./fixtures/
# No web server or ingress port is required for this command-line sample.
# Keep the task alive for instructor-approved ECS Exec sessions.
CMD ["sleep", "infinity"]
