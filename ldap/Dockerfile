FROM debian:trixie-20261104-slim

RUN apt-get update \
    && printf 'slapd slapd/no_configuration boolean true\n' \
       | debconf-set-selections \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
       --no-install-recommends \
       slapd \
       ldap-utils \
    && rm -rf /var/lib/apt/lists/*

RUN install -d -o openldap -g openldap \
    /var/lib/ldap \
    /run/slapd

COPY slapd.conf.template bootstrap.ldif.template /opt/ldap/

COPY --chmod=755 entrypoint.sh /usr/local/bin/ldap-entrypoint

ENTRYPOINT ["/usr/local/bin/ldap-entrypoint"]
