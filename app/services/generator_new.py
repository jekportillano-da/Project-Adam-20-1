from openai import OpenAI
from flask import current_app

class BudgetTipGenerator:
    def __init__(self):
        """Initialize the OpenAI client with Groq configuration"""
        api_key = current_app.config.get('GROQ_API_KEY')
        if not api_key:
            current_app.logger.error("Groq API key not found in app config")
            raise ValueError("Groq API key not configured")

        current_app.logger.info("Initializing Groq client...")
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            current_app.logger.info("Groq client initialized successfully")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Groq client: {str(e)}")
            raise

    def generate_tip(self, daily_budget: float, monthly_budget: float) -> str:
        """Generate a budget tip using the Groq API"""
        if not isinstance(daily_budget, (int, float)) or not isinstance(monthly_budget, (int, float)):
            current_app.logger.error(f"Invalid budget types: daily={type(daily_budget)}, monthly={type(monthly_budget)}")
            raise TypeError("Budget values must be numbers")

        if daily_budget < 0 or monthly_budget < 0:
            current_app.logger.error(f"Negative budget values: daily={daily_budget}, monthly={monthly_budget}")
            raise ValueError("Budget values cannot be negative")

        prompt = self._create_prompt(daily_budget, monthly_budget)
        
        try:
            current_app.logger.info("Sending request to Groq API...")
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a financial advisor in the Philippines. Provide exactly 3 money-saving tips, each with a title, one specific action, and realistic peso savings amounts. Format all peso amounts as 'PHP X.00'. Use bullet points with '•'. Keep language simple and practical."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            current_app.logger.debug("API Response received")
            
            if not response.choices:
                raise ValueError("No response choices returned from API")
                
            content = response.choices[0].message.content
            if not content or not content.strip():
                raise ValueError("Empty response content from API")
                
            current_app.logger.info("Successfully generated budget advice")
            return content.strip()
            
        except (ConnectionError, TimeoutError) as e:
            error_msg = f"Network error while calling Groq API: {str(e)}"
            current_app.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
            
        except ValueError as validation_error:
            current_app.logger.error(f"Invalid API response: {str(validation_error)}")
            raise validation_error

    def _create_prompt(self, daily_budget: float, monthly_budget: float) -> str:
        """Create the prompt for the Groq API"""
        return f"""With a daily budget of PHP {daily_budget:.2f} (PHP {monthly_budget:.2f} per month), provide 3 practical money-saving tips.

Format each tip exactly like this:

1. [Title of the tip]
• [One specific action to save money]
• Save PHP [X.00] to PHP [Y.00] per [day/week/month]"""
