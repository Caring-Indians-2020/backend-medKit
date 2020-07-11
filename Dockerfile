FROM python:3

# RUN apt-get update
# RUN apt-get install -y python3
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY ./ .
CMD [ "python","main.py" ]