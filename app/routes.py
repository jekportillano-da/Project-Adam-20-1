from flask import Blueprint, jsonify, render_template, request, current_app
from app.services.generator import BudgetTipGenerator
import re
from re import finditer
import logging

bp = Blueprint('budget', __name__)

def format_currency(amount):
    """Format amount as Philippine Peso"""
    return f"PHP {amount:,.2f}"

@bp.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

@bp.route('/api/tip', methods=['POST'])
def get_tip():
    """Generate a budget tip based on user input"""
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            current_app.logger.error("No JSON data received")
            return jsonify({'tip': 'Invalid request data'}), 400

        current_app.logger.debug(f"Received data: {data}")
        
        # Get and validate budget
        budget_str = str(data.get('budget', '')).replace(',', '')
        try:
            budget = float(budget_str)
        except (ValueError, TypeError):
            current_app.logger.error(f"Invalid budget value: {budget_str}")
            return jsonify({'tip': 'Please enter a valid amount'}), 400

        # Validate budget range
        if budget <= 0:
            return jsonify({'tip': 'Please enter a positive amount'}), 400
        if budget > 1000000:
            return jsonify({'tip': 'Amount cannot exceed PHP 1,000,000'}), 400

        # Get duration and calculate budgets
        duration = data.get('duration', 'monthly').lower()
        current_app.logger.info(f"Processing budget request: {budget} {duration}")

        # Convert budgets based on duration
        if duration == 'weekly':
            daily_budget = round(budget / 7, 2)
            monthly_budget = daily_budget * 30
        elif duration == 'monthly':
            daily_budget = round(budget / 30, 2) 
            monthly_budget = budget
        else:  # daily
            daily_budget = budget
            monthly_budget = daily_budget * 30

        current_app.logger.debug(f"Converted budgets - Daily: {format_currency(daily_budget)}, Monthly: {format_currency(monthly_budget)}")
        
        # Generate budget tip
        generator = BudgetTipGenerator()
        tip_text = generator.generate_tip(daily_budget, monthly_budget)
        current_app.logger.info("Raw response from generator:")
        current_app.logger.info(tip_text)
        
        if not tip_text or not tip_text.strip():
            current_app.logger.error("Received empty response from generator")
            return jsonify({'tip': 'Unable to generate budget advice at the moment. Please try again.'}), 500

        current_app.logger.info("Successfully generated budget advice")
        # Log the response structure
        lines = tip_text.strip().split('\n')
        current_app.logger.info("Response structure:")
        for i, line in enumerate(lines):
            current_app.logger.info(f"Line {i+1}: {line}")
        
        # Format currency values in response
        formatted_text = tip_text
        current_app.logger.debug(f"Original tip text: {tip_text}")
        
        try:
            # Only format numbers that come after "PHP"
            currency_pattern = r'PHP\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
            for match in finditer(currency_pattern, tip_text):
                try:
                    # Get the full match (including PHP) and the number group
                    full_match = match.group(0)
                    number_part = match.group(1)
                    
                    # Convert to float and format
                    amount = float(number_part.replace(',', ''))
                    formatted_currency = format_currency(amount)
                    
                    # Replace the entire match (including PHP) with the formatted version
                    formatted_text = formatted_text.replace(full_match, formatted_currency)
                except (ValueError, TypeError) as e:
                    current_app.logger.warning(f"Error formatting specific amount {match.group(0)}: {str(e)}")
                    continue
                    
            current_app.logger.debug(f"Formatted text: {formatted_text}")
        except Exception as e:
            current_app.logger.warning(f"Error during currency formatting: {str(e)}")
            # If formatting fails, return the original text
            formatted_text = tip_text

        return jsonify({'tip': formatted_text})

    except ValueError as ve:
        current_app.logger.error(f"Validation error: {str(ve)}")
        return jsonify({
            'tip': 'Unable to process your request. Please try again.'
        }), 400
        
    except RuntimeError as re:
        error_msg = str(re).lower()
        current_app.logger.error(f"Runtime error: {str(re)}")
        
        if 'network' in error_msg:
            status_code = 503
            message = 'Unable to connect to the service. Please try again later.'
        elif 'api key' in error_msg:
            status_code = 503
            message = 'The service is temporarily unavailable. Please try again later.'
        else:
            status_code = 500
            message = 'An unexpected error occurred. Please try again later.'
            
        return jsonify({'tip': message}), status_code
            
    except Exception as e:
        current_app.logger.exception("Unexpected error in get_tip")
        return jsonify({
            'tip': 'An unexpected error occurred. Please try again later.'
        }), 500
