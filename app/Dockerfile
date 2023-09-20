# pull official base image
FROM python:3.9.6-alpine

# set work directory
WORKDIR /usr/src/app

RUN apk update && apk add nmap && apk add nmap-scripts

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install relational database dependemcy 
RUN apk update && apk add musl-dev mariadb-dev gcc

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install wheel
RUN pip install mysqlclient
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/local/bin/
RUN sed -i 's/\r$//g' /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh


# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]