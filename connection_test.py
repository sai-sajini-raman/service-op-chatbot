import weaviate

# Connect using HTTP only
client = weaviate.connect_to_local(
    host="localhost",
    port=8080,
    skip_init_checks=True  # skip gRPC ping
)

try:
    if client.is_ready():
        print("✅ Connected to Weaviate successfully!")
    else:
        print("❌ Weaviate is not ready.")
except Exception as e:
    print("❌ Failed to connect:", e)
finally:
    client.close()
