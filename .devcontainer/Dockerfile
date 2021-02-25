FROM python:3-buster
COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN apt update && apt upgrade -y
RUN apt install whiptail -y
RUN pip install -r requirements.txt
