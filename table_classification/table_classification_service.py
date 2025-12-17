from flask import Flask, request, jsonify
import torch
import io
import datetime
import os
from PIL import Image
import torchvision.transforms as transforms

app = Flask(__name__)

class TableClassifier:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'models', 'table_model.pt')
        self.model = torch.jit.load(model_path, map_location='cpu')
        self.model.eval()
    
    def predict(self, image_file):
        try:
            image = Image.open(io.BytesIO(image_file.read())).convert('RGB')
            
            image = image.resize((280, 280))
            transform = transforms.ToTensor()
            tensor = transform(image).unsqueeze(0)
            
            with torch.no_grad():
                logits, probabilities = self.model(tensor)
                probs = probabilities[0] 
                
                clean_prob = probs[0].item()
                dirty_prob = probs[1].item()
                
                is_clean = clean_prob > dirty_prob
                confidence = clean_prob if is_clean else dirty_prob
                
                return {
                    'prediction': 'clean' if is_clean else 'dirty',
                    'confidence': round(confidence, 3),
                    'probabilities': {
                        'clean': round(clean_prob, 3),
                        'dirty': round(dirty_prob, 3)
                    }
                }
            
        except Exception as e:
            return {'error': str(e)}

classifier = TableClassifier()

@app.route('/api/classify', methods=['POST'])
def classify_table():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file'}), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        result = classifier.predict(image_file)
        
        if 'error' in result:
            return jsonify({'status': 'error', 'message': result['error']}), 500
        
        return jsonify({
            'status': 'success',
            **result,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    