from flask import Blueprint, request, jsonify, send_file
from functools import wraps
from datetime import datetime
from pathlib import Path
import os
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from model import PriceEstimationModel
from utils import calculate_cost_breakdown, generate_pdf_report

# Create Blueprint
price_estimation_bp = Blueprint('price_estimation', __name__, url_prefix='/api')

# Initialize model
price_model = None

def get_model():
    """Get or initialize the price model"""
    global price_model
    if price_model is None:
        price_model = PriceEstimationModel()
        # Try to load existing model
        try:
            price_model.load()
        except FileNotFoundError:
            print("Warning: Pre-trained model not found. Setup price estimation module first.")
    return price_model

def require_user_role(f):
    """Decorator to check if user has 'user' role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if authorization header exists
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Unauthorized: No token provided'}), 401
        
        # Check if user role is in request context
        user_role = request.headers.get('X-User-Role')
        if user_role != 'user':
            return jsonify({'error': 'Forbidden: Only users can access price estimation'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@price_estimation_bp.route('/estimate-price', methods=['POST'])
@require_user_role
def estimate_price():
    """
    Estimate gear price based on input specifications
    
    Expected JSON:
    {
        "gear_type": "Spur",
        "gearbox_type": "Industrial",
        "material": "Steel",
        "module": 2.5,
        "teeth": 50,
        "load": 1000,
        "speed": 1200,
        "gear_ratio": 2.5,
        "heat_treatment": true,
        "surface_finish": "Ground",
        "quantity": 10,
        "delivery_type": "Normal"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['gear_type', 'gearbox_type', 'material', 'module', 'teeth', 
                          'load', 'speed', 'gear_ratio', 'quantity', 'delivery_type']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get model and predict
        model = get_model()
        predicted_price = model.predict(data)
        
        # Calculate cost breakdown
        breakdown = calculate_cost_breakdown(predicted_price * 0.7, data)
        breakdown['total'] = predicted_price
        
        return jsonify({
            'status': 'success',
            'estimated_price': round(predicted_price, 2),
            'cost_breakdown': breakdown,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@price_estimation_bp.route('/generate-pdf', methods=['POST'])
@require_user_role
def generate_pdf():
    """
    Generate PDF report for price estimation
    
    Expected JSON:
    {
        "input_data": {...},
        "price_estimate": 1234.56,
        "cost_breakdown": {...}
    }
    """
    try:
        data = request.get_json()
        
        input_data = data.get('input_data', {})
        price_estimate = data.get('price_estimate', 0)
        cost_breakdown = data.get('cost_breakdown', {})
        
        # Generate PDF in memory
        pdf_buffer = generate_pdf_report(input_data, price_estimate, cost_breakdown)
        
        # Return PDF
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"gear_price_estimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@price_estimation_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    model = get_model()
    model_loaded = model.model is not None
    
    return jsonify({
        'status': 'ok' if model_loaded else 'model_not_loaded',
        'model_available': model_loaded,
        'timestamp': datetime.now().isoformat()
    }), 200

@price_estimation_bp.route('/estimate-price-batch', methods=['POST'])
@require_user_role
def estimate_price_batch():
    """
    Estimate prices for multiple gear specifications in batch
    
    Expected JSON:
    {
        "items": [
            {...gear_spec_1...},
            {...gear_spec_2...}
        ]
    }
    """
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({'error': 'No items provided'}), 400
        
        model = get_model()
        results = []
        
        for item in items:
            try:
                predicted_price = model.predict(item)
                breakdown = calculate_cost_breakdown(predicted_price * 0.7, item)
                breakdown['total'] = predicted_price
                
                results.append({
                    'gear_spec': item,
                    'estimated_price': round(predicted_price, 2),
                    'cost_breakdown': breakdown,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'gear_spec': item,
                    'error': str(e),
                    'status': 'error'
                })
        
        return jsonify({
            'status': 'success',
            'results': results,
            'total_items': len(items),
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'error'])
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500
