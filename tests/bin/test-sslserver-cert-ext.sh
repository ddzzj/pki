#!/bin/bash -e

INPUT=$1

if [ "$INPUT" = "" ]; then
    INPUT=sslserver.crt
fi

openssl x509 -text -noout -in $INPUT | tee output

# verfiy SKI extension
echo "X509v3 Subject Key Identifier: " > expected
sed -En 's/^ *(X509v3 Subject Key Identifier: .*)$/\1/p' output | tee actual
diff actual expected

# verfiy AKI extension
echo "X509v3 Authority Key Identifier: " > expected
sed -En 's/^ *(X509v3 Authority Key Identifier: .*)$/\1/p' output | tee actual
diff actual expected

# verfiy basic constraints extension
echo "X509v3 Basic Constraints: critical" > expected
echo "CA:FALSE" >> expected
sed -En 'N; s/^ *(X509v3 Basic Constraints: .*)\n *(.*)$/\1\n\2/p; D' output | tee actual
diff actual expected

# verfiy key usage extension
echo "X509v3 Key Usage: critical" > expected
echo "Digital Signature, Key Encipherment" >> expected
sed -En 'N; s/^ *(X509v3 Key Usage: .*)\n *(.*)$/\1\n\2/p; D' output | tee actual
diff actual expected

# verfiy extended key usage extension
echo "X509v3 Extended Key Usage: " > expected
echo "TLS Web Server Authentication, TLS Web Client Authentication" >> expected
sed -En 'N; s/^ *(X509v3 Extended Key Usage: .*)\n *(.*)$/\1\n\2/p; D' output | tee actual
diff actual expected

# verfiy SAN extension
echo "X509v3 Subject Alternative Name: " > expected
echo "DNS:pki.example.com" >> expected
sed -En 'N; s/^ *(X509v3 Subject Alternative Name: .*)\n *(.*)$/\1\n\2/p; D' output | tee actual
diff actual expected
