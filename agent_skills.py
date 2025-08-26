# Agent Skills - Special Abilities for the Voice Agent
# Day 25: Adding web search and weather capabilities

import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Tavily web search client
try:
    from tavily import TavilyClient
    TAVILY_CLIENT = TavilyClient(api_key=os.getenv("TAVILY_API_KEY")) if os.getenv("TAVILY_API_KEY") and os.getenv("TAVILY_API_KEY") != "YOUR_TAVILY_API_KEY" else None
except Exception as e:
    print(f"⚠️ Warning: Could not initialize Tavily client: {e}")
    TAVILY_CLIENT = None

# Weather API configuration - Using WeatherAPI.com (free, no payment details required)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_BASE_URL = "http://api.weatherapi.com/v1"

def search_web(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search the web using Tavily API
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary containing search results and metadata
    """
    print(f"🔍 SKILL: Web Search - Searching for: '{query}'")
    
    if not TAVILY_CLIENT:
        error_msg = "Web search unavailable - Tavily API key not configured"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "query": query,
            "results": []
        }
    
    try:
        # Perform the search
        response = TAVILY_CLIENT.search(
            query=query,
            max_results=max_results,
            include_answer=True,
            include_raw_content=False
        )
        
        # Format the results
        formatted_results = []
        if response.get('results'):
            for result in response['results'][:max_results]:
                formatted_results.append({
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "content": result.get('content', '')[:500] + "..." if len(result.get('content', '')) > 500 else result.get('content', ''),
                    "score": result.get('score', 0)
                })
        
        search_result = {
            "success": True,
            "query": query,
            "answer": response.get('answer', ''),
            "results": formatted_results,
            "total_results": len(formatted_results),
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ SKILL: Web Search - Found {len(formatted_results)} results")
        if response.get('answer'):
            print(f"📝 SKILL: Web Search - Quick Answer: {response['answer'][:200]}...")
        
        return search_result
        
    except Exception as e:
        error_msg = f"Web search failed: {str(e)}"
        print(f"❌ SKILL: Web Search - {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "query": query,
            "results": []
        }

def get_current_weather(location: str, units: str = "celsius") -> Dict[str, Any]:
    """
    Get current weather for a location using WeatherAPI.com (free, no payment details required)
    
    Args:
        location: City name or location
        units: Temperature units (celsius, fahrenheit)
        
    Returns:
        Dictionary containing weather information
    """
    print(f"🌤️ SKILL: Weather - Getting weather for: '{location}'")
    
    if not WEATHER_API_KEY or WEATHER_API_KEY == "YOUR_WEATHER_API_KEY":
        error_msg = "Weather service unavailable - WeatherAPI.com API key not configured"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "location": location
        }
    
    try:
        # Make API request to WeatherAPI.com
        url = f"{WEATHER_API_BASE_URL}/current.json"
        params = {
            "key": WEATHER_API_KEY,
            "q": location,
            "aqi": "no"  # Don't need air quality data
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert temperature based on units preference
        temp_c = data['current']['temp_c']
        temp_f = data['current']['temp_f']
        feels_like_c = data['current']['feelslike_c']
        feels_like_f = data['current']['feelslike_f']
        
        current_temp = temp_c if units.lower() == "celsius" else temp_f
        feels_like = feels_like_c if units.lower() == "celsius" else feels_like_f
        temp_units = "°C" if units.lower() == "celsius" else "°F"
        
        # Extract weather information
        weather_result = {
            "success": True,
            "location": {
                "name": data['location']['name'],
                "region": data['location']['region'],
                "country": data['location']['country'],
                "coordinates": {
                    "lat": data['location']['lat'],
                    "lon": data['location']['lon']
                },
                "timezone": data['location']['tz_id'],
                "local_time": data['location']['localtime']
            },
            "weather": {
                "main": data['current']['condition']['text'],
                "description": data['current']['condition']['text'],
                "icon": data['current']['condition']['icon'],
                "code": data['current']['condition']['code']
            },
            "temperature": {
                "current": round(current_temp, 1),
                "feels_like": round(feels_like, 1),
                "units": temp_units
            },
            "humidity": data['current']['humidity'],
            "pressure": data['current']['pressure_mb'],
            "visibility": data['current']['vis_km'],
            "uv_index": data['current']['uv'],
            "wind": {
                "speed_kph": data['current']['wind_kph'],
                "speed_mph": data['current']['wind_mph'],
                "direction": data['current']['wind_degree'],
                "direction_text": data['current']['wind_dir']
            },
            "timestamp": datetime.now().isoformat(),
            "last_updated": data['current']['last_updated']
        }
        
        location_name = data['location']['name']
        country = data['location']['country']
        condition = data['current']['condition']['text']
        print(f"✅ SKILL: Weather - {location_name}, {country}: {current_temp}{temp_units}, {condition}")
        
        return weather_result
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            error_msg = f"Location '{location}' not found"
        else:
            error_msg = f"Weather API error: {e}"
        print(f"❌ SKILL: Weather - {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "location": location
        }
    except Exception as e:
        error_msg = f"Weather service failed: {str(e)}"
        print(f"❌ SKILL: Weather - {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "location": location
        }

def get_weather_forecast(location: str, days: int = 5, units: str = "celsius") -> Dict[str, Any]:
    """
    Get weather forecast for a location using WeatherAPI.com
    
    Args:
        location: City name or location
        days: Number of days for forecast (1-10, free tier supports up to 3 days)
        units: Temperature units (celsius, fahrenheit)
        
    Returns:
        Dictionary containing forecast information
    """
    # Limit days to 3 for free tier
    days = min(days, 3)
    print(f"🌤️ SKILL: Weather Forecast - Getting {days}-day forecast for: '{location}'")
    
    if not WEATHER_API_KEY or WEATHER_API_KEY == "YOUR_WEATHER_API_KEY":
        error_msg = "Weather service unavailable - WeatherAPI.com API key not configured"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "location": location
        }
    
    try:
        # Make API request to WeatherAPI.com forecast endpoint
        url = f"{WEATHER_API_BASE_URL}/forecast.json"
        params = {
            "key": WEATHER_API_KEY,
            "q": location,
            "days": days,
            "aqi": "no",
            "alerts": "no"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Format forecast results
        forecast_days = []
        for day_data in data['forecast']['forecastday']:
            date = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
            
            # Get temperature values based on units preference
            if units.lower() == "celsius":
                min_temp = round(day_data['day']['mintemp_c'], 1)
                max_temp = round(day_data['day']['maxtemp_c'], 1)
                avg_temp = round(day_data['day']['avgtemp_c'], 1)
                temp_units = "°C"
            else:
                min_temp = round(day_data['day']['mintemp_f'], 1)
                max_temp = round(day_data['day']['maxtemp_f'], 1)
                avg_temp = round(day_data['day']['avgtemp_f'], 1)
                temp_units = "°F"
            
            forecast_days.append({
                "date": date.isoformat(),
                "day_name": date.strftime("%A"),
                "weather": {
                    "main": day_data['day']['condition']['text'],
                    "description": day_data['day']['condition']['text'],
                    "icon": day_data['day']['condition']['icon'],
                    "code": day_data['day']['condition']['code']
                },
                "temperature": {
                    "min": min_temp,
                    "max": max_temp,
                    "avg": avg_temp,
                    "units": temp_units
                },
                "humidity": day_data['day']['avghumidity'],
                "wind_speed": {
                    "kph": day_data['day']['maxwind_kph'],
                    "mph": day_data['day']['maxwind_mph']
                },
                "precipitation": {
                    "total_mm": day_data['day']['totalprecip_mm'],
                    "total_in": day_data['day']['totalprecip_in'],
                    "chance_rain": day_data['day']['daily_chance_of_rain'],
                    "chance_snow": day_data['day']['daily_chance_of_snow']
                },
                "uv_index": day_data['day']['uv'],
                "sunrise": day_data['astro']['sunrise'],
                "sunset": day_data['astro']['sunset']
            })
        
        forecast_result = {
            "success": True,
            "location": {
                "name": data['location']['name'],
                "region": data['location']['region'],
                "country": data['location']['country'],
                "coordinates": {
                    "lat": data['location']['lat'],
                    "lon": data['location']['lon']
                },
                "timezone": data['location']['tz_id'],
                "local_time": data['location']['localtime']
            },
            "forecast": forecast_days,
            "days_requested": days,
            "timestamp": datetime.now().isoformat()
        }
        
        location_name = data['location']['name']
        country = data['location']['country']
        print(f"✅ SKILL: Weather Forecast - {days}-day forecast for {location_name}, {country}")
        
        return forecast_result
        
    except Exception as e:
        error_msg = f"Weather forecast failed: {str(e)}"
        print(f"❌ SKILL: Weather Forecast - {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "location": location
        }

# Function declarations for Gemini LLM integration
SKILL_FUNCTION_DECLARATIONS = [
    {
        "name": "search_web",
        "description": "Search the web for current information, news, facts, or any topic. Use this when you need up-to-date information that you don't have in your training data.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query or question to search for"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_current_weather",
        "description": "Get the current weather conditions for any location in the world.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name, location, or address to get weather for (e.g., 'London', 'New York', 'Tokyo')"
                },
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature units to use (default: celsius)",
                    "default": "celsius"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_weather_forecast",
        "description": "Get weather forecast for multiple days for any location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name, location, or address to get forecast for"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days for the forecast (1-5, default: 5)",
                    "default": 5
                },
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature units to use (default: celsius)",
                    "default": "celsius"
                }
            },
            "required": ["location"]
        }
    }
]

# Function mapping for execution
SKILL_FUNCTIONS = {
    "search_web": search_web,
    "get_current_weather": get_current_weather,
    "get_weather_forecast": get_weather_forecast
}

def execute_skill_function(function_name: str, function_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a skill function by name with provided arguments
    
    Args:
        function_name: Name of the function to execute
        function_args: Arguments to pass to the function
        
    Returns:
        Result from the function execution
    """
    if function_name not in SKILL_FUNCTIONS:
        return {
            "success": False,
            "error": f"Unknown skill function: {function_name}"
        }
    
    try:
        function = SKILL_FUNCTIONS[function_name]
        result = function(**function_args)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Error executing {function_name}: {str(e)}"
        }

if __name__ == "__main__":
    # Test the skills
    print("Testing Agent Skills...")
    
    # Test web search
    print("\n" + "="*50)
    search_result = search_web("What is the latest news about AI in 2024?", 3)
    print(f"Search Result: {json.dumps(search_result, indent=2)}")
    
    # Test weather
    print("\n" + "="*50)
    weather_result = get_current_weather("London")
    print(f"Weather Result: {json.dumps(weather_result, indent=2)}")
    
    # Test forecast
    print("\n" + "="*50)
    forecast_result = get_weather_forecast("New York", 3)
    print(f"Forecast Result: {json.dumps(forecast_result, indent=2)}")
