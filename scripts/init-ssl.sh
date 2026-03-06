#!/bin/bash
# Generate self-signed SSL certificates for development/testing
# For production, use Let's Encrypt (certbot)
#
# Usage: ./scripts/init-ssl.sh [domain]
# Production: certbot certonly --webroot -w /var/www/certbot -d yourdomain.com

set -euo pipefail

DOMAIN="${1:-localhost}"
SSL_DIR="./nginx/ssl"

mkdir -p "$SSL_DIR"

if [ -f "$SSL_DIR/cert.pem" ] && [ -f "$SSL_DIR/key.pem" ]; then
    echo "SSL certificates already exist in $SSL_DIR"
    echo "Delete them first if you want to regenerate."
    exit 0
fi

echo "Generating self-signed SSL certificate for: $DOMAIN"

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$SSL_DIR/key.pem" \
    -out "$SSL_DIR/cert.pem" \
    -subj "/C=VN/ST=HCMC/L=HCMC/O=SEO Dashboard/CN=$DOMAIN" \
    2>/dev/null

echo "Done! Certificates created:"
echo "  Certificate: $SSL_DIR/cert.pem"
echo "  Private key: $SSL_DIR/key.pem"
echo ""
echo "For production, use Let's Encrypt instead:"
echo "  certbot certonly --webroot -w /var/www/certbot -d $DOMAIN"
