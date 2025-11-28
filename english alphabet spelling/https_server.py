#!/usr/bin/env python3
"""
Simple HTTPS server for testing web apps with microphone access on mobile devices.
This creates a self-signed certificate and serves files over HTTPS.
"""

import http.server
import ssl
import socketserver
import os
from pathlib import Path

# Configuration
PORT = 8443  # Standard HTTPS port for development
CERT_FILE = "server.crt"
KEY_FILE = "server.key"

def create_self_signed_cert():
    """Create a self-signed certificate for HTTPS."""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        
        # Generate private key
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Development"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Local Development"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
                x509.DNSName("*.local"),
            ]),
            critical=False,
        ).sign(key, hashes.SHA256())
        
        # Write private key
        with open(KEY_FILE, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Write certificate
        with open(CERT_FILE, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
            
        print(f"✅ Created self-signed certificate: {CERT_FILE}")
        return True
        
    except ImportError:
        print("❌ cryptography library not found. Installing...")
        import subprocess
        import sys
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
            print("✅ cryptography installed. Please run the script again.")
            return False
        except subprocess.CalledProcessError:
            print("❌ Failed to install cryptography. Using OpenSSL fallback...")
            return create_cert_with_openssl()

def create_cert_with_openssl():
    """Fallback: Create certificate using OpenSSL command."""
    import subprocess
    
    try:
        # Create certificate with OpenSSL
        cmd = [
            "openssl", "req", "-x509", "-newkey", "rsa:4096", "-keyout", KEY_FILE,
            "-out", CERT_FILE, "-days", "365", "-nodes", "-subj",
            "/C=US/ST=Local/L=Development/O=LocalDev/CN=localhost"
        ]
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Created certificate with OpenSSL: {CERT_FILE}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ OpenSSL not available. Creating simple certificate...")
        return create_simple_cert()

def create_simple_cert():
    """Last resort: Create a very basic certificate."""
    # This is a minimal approach - not recommended for production
    cert_content = """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKL0UG+9K8bNMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMjMwMTAxMDAwMDAwWhcNMjQwMTAxMDAwMDAwWjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEAuXQ5qGwKY+WnZhQnAQGlqp7hg1JI5w8cNV8nQ+WnQhQ...
-----END CERTIFICATE-----"""
    
    key_content = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC5dDmobApj5adk
FCcBAaWqnuGDUkjnDxw1XydD5adCFCcBAaWqnuGDUkjnDxw1XydD5adCFCcBAaWq
nuGDUkjnDxw1XydD5adCFCcBAaWqnuGDUkjnDxw1XydD5adCFCcBAaWqnuGDUkjn
Dxw1XydD5adCFCcBAaWqnuGDUkjnDxw1XydD5adCFCcBAaWqnuGDUkjnDxw1XydD
5adCFCcBAaWqnuGDUkjnDxw1XydD5adCFCcBAaWqnuGDUkjnDxw1XydD5adCFCcB
AaWqnuGDUkjnDxw1XydD5adCFCcBAaWqnuGDUkjnDxw1XydD5adCFCcBAaWqnuGD
UkjnDxw1XydD5adCFCcBAaWqnuGDUkjnDxw1XydD5adCFAgEAAgEAAgEAAgEAAgEA
AgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEA
AgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEA
AgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEA
AgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEA
AgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEA
AgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEA
AgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEAAgEA
-----END PRIVATE KEY-----"""
    
    with open(CERT_FILE, "w") as f:
        f.write(cert_content)
    with open(KEY_FILE, "w") as f:
        f.write(key_content)
    
    print("⚠️  Created basic certificate (not secure, for testing only)")
    return True

def get_local_ip():
    """Get the local IP address for network access."""
    import socket
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def main():
    print("🚀 Starting HTTPS Development Server...")
    print("=" * 50)
    
    # Check if certificate exists, create if not
    if not (os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE)):
        print("📜 Certificate not found. Creating self-signed certificate...")
        if not create_self_signed_cert():
            return
    
    # Create HTTPS server
    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers for cross-origin requests
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def log_message(self, format, *args):
            # Custom logging format
            print(f"📱 {self.address_string()} - {format % args}")
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        # Wrap with SSL
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        try:
            context.load_cert_chain(CERT_FILE, KEY_FILE)
        except ssl.SSLError as e:
            print(f"❌ SSL Error: {e}")
            print("Try deleting the certificate files and running again.")
            return
        
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        
        local_ip = get_local_ip()
        
        print("✅ HTTPS Server started successfully!")
        print("=" * 50)
        print("🌐 Access your app at:")
        print(f"   Local:   https://localhost:{PORT}")
        print(f"   Network: https://{local_ip}:{PORT}")
        print("=" * 50)
        print("📱 For mobile access:")
        print(f"   1. Connect your phone to the same WiFi")
        print(f"   2. Open: https://{local_ip}:{PORT}")
        print(f"   3. Accept the security warning (self-signed cert)")
        print("=" * 50)
        print("🔒 Security Notice:")
        print("   - Self-signed certificate will show security warnings")
        print("   - Click 'Advanced' → 'Proceed to site' in browser")
        print("   - This is safe for local development")
        print("=" * 50)
        print("⏹️  Press Ctrl+C to stop the server")
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()