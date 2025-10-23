import base64
key_pair = "pk-lf-b2b2f57c-6d8c-4a30-b583-4d1231a209c8:sk-lf-2849466e-e714-4e71-b29f-07d9a9126bfc"
auth = base64.b64encode(key_pair.encode()).decode()
print(f"Authorization: Basic {auth}")