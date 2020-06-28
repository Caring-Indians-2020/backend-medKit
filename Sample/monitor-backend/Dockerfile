FROM python

# RUN apt-get update
# RUN apt-get install -y python3
COPY . .
RUN pip3 install -r requirements.txt
CMD [ "python","main.py" ]