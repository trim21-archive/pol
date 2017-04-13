FROM tiangolo/uwsgi-nginx:python3.5

MAINTAINER Sebastian Ramirez <tiangolo@gmail.com>

RUN pip install flask ics requests beautifulsoup4 pytz -U

# Add app configuration to Nginx
COPY nginx.conf /etc/nginx/conf.d/

# Copy sample app
COPY ./app /app
