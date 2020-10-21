FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1

# Install nginx
RUN apt --yes update
RUN apt --yes install nginx

# Install app package
WORKDIR /service-lib
COPY  ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn==19.9.0 gevent==20.6.2

# Mount source code
WORKDIR /sale-portal-api
RUN mkdir log && mkdir media && mkdir media/images && mkdir media/excel
COPY  . .
RUN python manage.py collectstatic --noinput
#RUN python manage.py migrate --database=default && python manage.py collectstatic --noinput
COPY  ./nginx.conf /etc/nginx/conf.d/default.conf

# For security, avoid zombie process
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

RUN groupadd --gid 5000 nonroot \
    && useradd --home-dir /home/nonroot --create-home --uid 5000 \
    --gid 5000 --shell /bin/sh --skel /dev/null nonroot

# Run app
EXPOSE 8001
CMD ["/bin/sh","-c", "/etc/init.d/nginx restart && gunicorn --workers 1 --bind 0.0.0.0:8002 sale_portal.wsgi:application"]
