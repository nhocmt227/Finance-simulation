FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Make sure setup script is executable and run it
RUN apt-get update && apt-get install -y dos2unix
RUN dos2unix ./setup/setup.sh
RUN chmod +x ./setup/setup.sh
RUN bash ./setup/setup.sh

EXPOSE 9000

CMD ["python", "main.py"]