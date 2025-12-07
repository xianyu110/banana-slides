"""
Default API Configuration
These keys are built-in defaults to enable zero-configuration deployment.
Users can override these by setting environment variables in .env file.
"""

# Built-in default API keys for text generation
# Get yours at: https://aistudio.google.com/app/apikey
DEFAULT_TEXT_API_KEY = "AIzaSyBn7QSorvokHlLRv7lj3-BKoE0okwYqz2w"
DEFAULT_TEXT_API_BASE = "https://generativelanguage.googleapis.com"

# Built-in default API keys for image generation
# Third-party proxy with OpenAI-compatible format
DEFAULT_IMAGE_API_KEY = "sk-HfmbZPrN2kWSJd0AJrS85xNBNeP0KKE45S0IjkrWAWavdBz8"
DEFAULT_IMAGE_API_BASE = "https://apipro.maynor1024.live"

# Built-in MinerU token for document parsing
# Get yours at: https://mineru.net
DEFAULT_MINERU_TOKEN = "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI3MzQwMDc1NyIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc2NTA3ODU5NiwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTMzNDY0MDgzMDYiLCJvcGVuSWQiOm51bGwsInV1aWQiOiIxZjEyZjZhYy0xMmU1LTQ4OWUtODlmMC0xNjhiMGMzOTJlNDQiLCJlbWFpbCI6IiIsImV4cCI6MTc2NjI4ODE5Nn0.pQP77iUZOo9JrDKqvnCeULMFP6bPsu-imbdf2CB5kU6ECVBIZ3_8cbaXBBehRyc8sJjAFetS4vQgIDRvvecyTA"
DEFAULT_MINERU_API_BASE = "https://mineru.net"

# Note: These are shared demo keys with limited quota.
# For production use, please:
# 1. Get your own API keys
# 2. Set them in .env file or environment variables
# 3. Restart the application
