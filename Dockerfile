FROM tiangolo/uwsgi-nginx:python3.5

MAINTAINER Trim21 <Trim21me@gmail.com>

RUN pip install pip -U && \
 pip install flask sdu-bkjws beautifulsoup4 requests ics -U

# Add app configuration to Nginx
COPY nginx.conf /etc/nginx/conf.d/

# Copy sample app
COPY ./* /app/

