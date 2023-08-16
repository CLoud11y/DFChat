from enums import API_MODE

SECRET_KEY = "yoursecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7

api_type = API_MODE.AZURE
# Azure mode config
api_url = "https://xxxx.openai.azure.com/" 
api_key = "your key from azure"
api_version = "2023-03-15-preview"
completion_engine_gpt4 = "yourdeployment"
completion_engine_gpt35= "yourdeployment"

openweathermap_api_key = "your key from openweathermap"