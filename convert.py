import requests, asyncio, os, io
from dotenv import load_dotenv
from googletrans import Translator 


# ---------ENV FILES---------
# tokenbot=YOUR_TOKEN_BOT
# API_KEY=YOUR_API_KEY_FOR_SPOONACULAR

load_dotenv()
translator = Translator()

async def convertTxt(nameProd):
    nameProd = await translator.translate(nameProd, dest="en")
    nameProd = nameProd.text.replace(' ', '+')
    print(nameProd)
    apiLink = "https://api.spoonacular.com/recipes/guessNutrition"
    apikey = os.getenv("API_KEY")
    params = {
        "apiKey":apikey,
        "title": nameProd
    }
    response = requests.get(apiLink, params=params)
    print(response.status_code)
    print(response.url)
    try:
        response = response.json()
        print(response)
        cal = response["calories"]["value"]
        fat = response["fat"]["value"]
        prt = response["protein"]["value"]
        crb = response["carbs"]["value"]
        return cal, prt, fat, crb
    except:
        return -1, -1, -1, -1
      
      
async def converImage(image):
    apiLink = "https://api.spoonacular.com/food/images/analyze"
    apikey = os.getenv("API_KEY")
    files = {
        "file": ('image.jpg', image.getvalue(), 'image/jpeg')
    }
    
    params = {
        "apiKey":apikey
    }
    response = requests.post(apiLink, params=params, files=files)
    try:
        resp = response.json()
        nut = resp["nutrition"]
        cal = nut["calories"]["value"]
        fat = nut["fat"]["value"]
        prt = nut["protein"]["value"]
        crb = nut["carbs"]["value"]
        name = resp["category"]["name"]
        name = await translator.translate(name, dest="ru")
        name = name.text
        print(name)
        return name, cal, fat, prt, crb
    except:
        return "undf", -1, -1, -1, -1
        
        
    
    