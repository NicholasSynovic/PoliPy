FROM python:3.9.1
COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN apt update && apt upgrade -y
RUN apt install whiptail -y
