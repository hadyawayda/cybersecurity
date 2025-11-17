FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends       nginx openssh-server tor tini python3 ca-certificates     && rm -rf /var/lib/apt/lists/*
RUN useradd -ms /bin/bash appuser
RUN mkdir -p /var/www/html /var/run/sshd /var/lib/tor/hidden_service &&     chown -R debian-tor:debian-tor /var/lib/tor && chmod 0700 /var/lib/tor/hidden_service
COPY nginx.conf /etc/nginx/nginx.conf
COPY sshd_config /etc/ssh/sshd_config
COPY torrc /etc/tor/torrc
COPY index.html /var/www/html/index.html
COPY entrypoint.py /usr/local/bin/entrypoint.py
RUN chmod +x /usr/local/bin/entrypoint.py
EXPOSE 80 4242
ENTRYPOINT ["/usr/bin/tini","--","/usr/local/bin/entrypoint.py"]
