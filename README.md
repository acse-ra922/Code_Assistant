# 💻 Code Analysis App

An enhanced Streamlit application that lets users input code snippets and receive detailed explanations/analysis using a language model. The app includes performance metrics, caching, error handling, and a user-friendly interface.

## Features

- **Code Analysis**: Get detailed explanations of code structure, purpose, and potential issues
- **Performance Metrics**: Track latency, token counts, and model performance
- **Model Selection**: Choose from available models in Ollama
- **Result Caching**: Fast retrieval of previous analyses
- **Analysis History**: Access your previous code analyses with one click
- **Error Handling**: Robust error management with automatic retries
- **Rate Limiting**: Prevents overloading the LLM service
- **Performance Analytics**: Visual tracking of latency over time

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install and start Ollama:
   - Follow instructions at [ollama.ai](https://ollama.ai) to install
   - Pull the codellama model: `ollama pull codellama`
   - Ensure Ollama is running locally

3. Run the app:
   ```
   streamlit run app.py
   ```

## Project Structure

- `app.py`: Main Streamlit application
- `llm_service.py`: LLM integration and code analysis logic
- `utils.py`: Helper functions for the UI and analytics
- `custom.css`: Custom styling for the application

## Changing the LLM Provider

The app is designed to make it easy to swap out the LLM provider:

1. Edit `llm_service.py`
2. Add a new function for your preferred LLM service
3. Update the `LLM_PROVIDER` variable at the top of the file
4. Implement the corresponding analysis function

## Current Limitations

- Requires Ollama to be running locally
- Limited to models available in Ollama
- Token count estimation is approximate

## Future Enhancements

- Add support for more LLM providers
- Implement user authentication
- Add code highlighting in results
- Support for analyzing multiple files
- Add export functionality for analyses