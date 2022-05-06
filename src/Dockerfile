# installing python
FROM python:3.7

# creating a directory/folder to put db.py in
RUN mkdir usr/app
WORKDIR usr/app

# copy everything in current directory into usr/app directory
COPY . .

# install requirements
RUN pip install -r requirements.txt

# only have one CMD in your dockerfile. It tells the computer 
# how you're gonna run the app
CMD python app.py