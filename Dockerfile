FROM python:3.13-alpine
WORKDIR /app
COPY app/ /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "stremality.py"]