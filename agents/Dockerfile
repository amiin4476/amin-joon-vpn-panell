
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN addgroup --system agentgroup && \
    adduser --system --ingroup agentgroup agentuser

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=agentuser:agentgroup main.py .

USER agentuser

EXPOSE 9000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
