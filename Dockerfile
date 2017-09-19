FROM tiangolo/uwsgi-nginx:python3.5

MAINTAINER Trim21 <Trim21me@gmail.com>

RUN pip install flask==0.12.2 beautifulsoup4==4.6.0 \
                requests==2.18.1 ics==0.3.1  icalendar==3.11.5
RUN pip install sdu-bkjws==1.0.7

# Add app configuration to Nginx
COPY nginx.conf /etc/nginx/conf.d/

# Copy sample app
COPY ./app /app


