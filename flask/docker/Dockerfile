#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM valkey/valkey:latest

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added

COPY service/valkey /etc/init.d/valkey
COPY docker/docker-entrypoint /usr/local/bin/
COPY docker/valkey.conf /etc/valkey/valkey.conf
COPY service/service /etc/systemd/system/valkey.service
COPY docker/init-functions /lib/lsb/init-functions
COPY demo.tar.gz /app.tar.gz
COPY sdk.tar.gz /usr/src/sdk.tar.gz
COPY main.py /demo/main.py
COPY .env /demo/.env

ARG DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
	\
	tar -xf /app.tar.gz -C /; \
	mv /demo/flask/app /demo/app; \
	rm -rf /app.tar.gz; rm -rf /demo/flask; \
	tar -xf /usr/src/sdk.tar.gz -C /usr/src/; \
	rm -rf /usr/src/sdk.tar.gz; \
	chmod +x /usr/local/bin/docker-entrypoint; \
	chmod +x /etc/init.d/valkey;

RUN set -eux; \
	\
	apt-get update; \
	DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
		debconf ca-certificates \
		python3 python3-pip python3-requests nano pkg-config \
		python3-dev default-libmysqlclient-dev build-essential \
		python3-cffi-backend python3-cryptography python3-cryptography-vectors \
		python3-async-timeout \
		python3-certifi \
		python3-cffi \
		python3-charset-normalizer \
		python3-click \
		python3-gevent \
		python3-greenlet \
		python3-idna \
		python3-pycparser \
		python3-tomli \
		python3-ujson \
		python3-urllib3 \
		python3-xxhash \
		python3-netifaces \
		python3-dotenv \
		python3-numpy \
	; \
	python3 -m pip install --break-system-packages \
		valkey libvalkey \
		fe25519 ge25519 \
		flask-minify password-validator email_validator redis \
		Flask Bootstrap-Flask webauthn Flask-SQLAlchemy Flask-Session \
		Flask-SocketIO Flask-Compress Flask-Mail \
		Flask-Login bleach mysqlclient; \
	python3 -m pip install --ignore-installed --break-system-packages /usr/src/sdk; \ 
	apt-get remove -y python3-pip build-essential && apt-get clean; \
	rm -rf /var/lib/apt/lists/*; rm -rf /usr/src/sdk;

RUN set -eux; \
	\
	mkdir /var/run/rdbms; \
	chown valkey:valkey /data; \
	chown valkey:valkey /var/run/rdbms;

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

VOLUME /data
WORKDIR /demo

EXPOSE 80 443 6379 6378

ENTRYPOINT ["docker-entrypoint"]
CMD ["/bin/bash", "-c"]