# Agent Skills Setup - Day 25

Meyme now has special skills! Your AI voice agent can search the web and get weather information.

## 🌟 Available Skills

### 1. **Web Search** 🔍
- Search the web for current information, news, facts, or any topic
- Powered by Tavily API
- Provides quick answers and detailed search results

### 2. **Weather Information** 🌤️
- Get current weather conditions for any location
- Get multi-day weather forecasts
- Powered by OpenWeatherMap API

## 🛠️ Setup Instructions

### Step 1: Get API Keys

#### Tavily API (Web Search)
1. Visit [https://app.tavily.com/](https://app.tavily.com/)
2. Sign up for a free account
3. Copy your API key from the dashboard
4. You get 1,000 free API credits every month

#### OpenWeatherMap API (Weather)
1. Visit [https://openweathermap.org/api](https://openweathermap.org/api)
2. Sign up for a free account
3. Go to "API keys" section
4. Copy your API key
5. Free tier includes 1,000 API calls per day

### Step 2: Configure Environment Variables

Edit your `.env` file and replace the placeholder values:

```bash
# Agent Skills API Keys
TAVILY_API_KEY="your_actual_tavily_api_key_here"
WEATHER_API_KEY="your_actual_openweathermap_api_key_here"
```

### Step 3: Test the Skills

Run the agent skills test:

```bash
python agent_skills.py
```

This will test both web search and weather functionality.

## 🎯 How It Works

### Voice Commands Examples

**Web Search:**
- "What's the latest news about AI?"
- "Search for information about quantum computing"
- "Tell me about recent developments in space exploration"

**Weather:**
- "What's the weather like in London?"
- "How's the weather in New York today?"
- "Give me the forecast for Tokyo this week"

### Function Calling Flow

1. **User speaks** → STT transcribes to text
2. **LLM analyzes** → Determines if skills are needed
3. **Skill activation** → Web search or weather API called
4. **Results processed** → Data formatted and returned
5. **LLM responds** → Natural language response with skill data
6. **TTS synthesis** → Response converted to speech

## 📊 Console Output

When skills are used, you'll see detailed console output:

```
🛠️ SKILL ACTIVATION: search_web
🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️
📞 Function: search_web
📋 Arguments: {"query": "latest AI news", "max_results": 5}
🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️🛠️

🔍 SKILL: Web Search - Searching for: 'latest AI news'
✅ SKILL: Web Search - Found 5 results
📝 SKILL: Web Search - Quick Answer: Recent AI developments include...

📊 SKILL RESULT:
📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊
✅ Skill executed successfully
🔍 Quick Answer: Recent AI developments include breakthrough in...
📊 Found 5 results
📊📊📊📊📊📊📊📊📊📊📊📊📊📊📊

🤖 FINAL RESPONSE (with skill data):
============================================================
Based on my search, here are the latest AI developments...
============================================================
```

## 🚨 Important Notes

- **API Keys Required**: Skills won't work without proper API keys
- **Free Tiers**: Both services offer generous free tiers
- **Rate Limits**: Be mindful of API rate limits
- **Error Handling**: Skills gracefully handle API failures
- **Console Logging**: All skill usage is logged for debugging

## 🔧 Customization

You can extend the skills by:

1. Adding new functions to `agent_skills.py`
2. Adding function declarations to `SKILL_FUNCTION_DECLARATIONS`
3. Updating the function mapping in `SKILL_FUNCTIONS`

## 📝 Troubleshooting

**Skills not working?**
- Check API keys in `.env` file
- Verify internet connection
- Check console logs for error messages
- Ensure API services are accessible

**Console shows skill activation but no results?**
- Verify API keys are valid
- Check if you've exceeded rate limits
- Review API service status pages

Your agent is now equipped with powerful skills! 🚀
