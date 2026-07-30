import requests

print("Testing requests library in sandbox...")
print(f"requests version: {requests.__version__}")

# Test that we can import and use requests
try:
    # Don't actually make a request, just test the import
    print("✓ requests imported successfully")
except Exception as e:
    print(f"✗ Error: {e}")
