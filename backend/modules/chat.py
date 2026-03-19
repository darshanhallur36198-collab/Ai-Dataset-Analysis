import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def chat_with_data(file_path: str, query: str, api_key: str = None) -> str:
    # Use provided API key or fallback to environment variable
    key_to_use = api_key or os.getenv("GOOGLE_API_KEY")
    if not key_to_use:
        return "Error: Please provide a Google Gemini API Key in the settings."

    try:
        genai.configure(api_key=key_to_use)
        # We can use gemini-1.5-flash as it's fast and has a large context window
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Test if model is accessible
            # We don't want to call it yet, so we just proceed
        except Exception:
            model = genai.GenerativeModel('gemini-pro')
        
        # Load dataset
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            elif file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
            else:
                return f"Error: Unsupported file format for chat ({file_path})."
        except Exception as e:
            return f"Error loading dataset: {str(e)}"
        
        # Prepare context payload
        # Limit the rows to prevent token exhaustion, but give enough for context
        row_limit = 1000  
        sample_df = df.head(row_limit)
        
        data_info = f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns.\n\n"
        data_info += f"Columns: {', '.join(df.columns.tolist())}\n\n"
        
        # We provide a rich summary (e.g. data types and descriptive stats)
        # for numbers so the LLM can see totals without seeing every row
        try:
            summary = df.describe().to_string()
            data_info += f"Numerical Summary:\n{summary}\n\n"
        except:
            pass
            
        # Give a substantial sample
        data_info += f"Data Sample (First {len(sample_df)} rows):\n"
        data_info += sample_df.to_csv(index=False)
        
        prompt = f"""You are an advanced AI Data Analyst. You are analyzing a dataset for a user.
Here is information about the dataset:
{data_info}

The user has asked the following question about the data:
"{query}"

Please answer the user's question clearly and concisely based on the data provided. 
If the data sample and summary provided do not contain enough information to fully answer the question (e.g., if there are too many rows missing from the sample), give the best answer you can from the summary, and briefly mention the limitation.
Format your answer with markdown. Avoid providing code unless asked. Direct, professional, and insightful.
"""

        print(f"[DEBUG] AI Prompt length: {len(prompt)} chars")
        
        try:
            response = model.generate_content(prompt)
        except Exception as e:
            if "404" in str(e):
                print("[INFO] gemini-1.5-flash not found, falling back to gemini-pro")
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
            else:
                raise e
        
        # Check if response has parts (avoid error on blocked content)
        if not response or not hasattr(response, 'text'):
             if hasattr(response, 'prompt_feedback'):
                 return f"AI Error: Your query or the data was blocked by safety filters. Details: {response.prompt_feedback}"
             return "AI Error: Received empty response from Gemini. Please try a simpler question."
             
        try:
            return response.text
        except ValueError:
            return "AI Error: The AI response was blocked by safety filters during generation."

    except Exception as e:
        print(f"[ERROR] Chat exception: {str(e)}")
        if "403" in str(e):
            return "AI Error (403): Gemini API Key is invalid or has insufficient permissions."
        if "429" in str(e):
            return "AI Error (429): Quota exceeded. Please wait a moment and try again."
        if "404" in str(e):
            return "AI Error (404): Model not found. Please ensure your Gemini API project has at least one active model."
        return f"AI Error: {str(e)}"
