from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import PyPDF2
import io
import re
import logging
from dotenv import load_dotenv
import torch
from transformers import pipeline

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app, 
     origins=[
         "http://localhost:5173",
         "https://email-classifier.vercel.app",
         "https://*.vercel.app",
         "https://email-sorter-pi.vercel.app"
     ],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

# Handler global para OPTIONS requests (CORS preflight)
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        return response

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração de upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Criar pasta de uploads
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Inicialização dos modelos Transformers
class TransformersClassifier:
    def __init__(self):
        self.sentiment_model = None
        self.zero_shot_classifier = None
        self.device = torch.device('cpu')  # Força CPU para estabilidade
        logger.info(f"Using device: {self.device}")
        
        self.initialize_models()
    
    def initialize_models(self):
        """Inicializa modelos Transformers com fallbacks robustos"""
        try:
            # Modelo de análise de sentimento (mais estável)
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                return_all_scores=True,
                device=-1  # Força CPU
            )
            logger.info("Sentiment analysis model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            
        try:
            # Modelo zero-shot para classificação específica
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1  # Força CPU
            )
            logger.info("Zero-shot classification model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load zero-shot model: {e}")

# Instância global do classificador
classifier = TransformersClassifier()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_stream):
    """Extrai texto de arquivo PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        raise Exception("Could not read PDF file")

def preprocess_text(text):
    """Pré-processamento robusto do texto"""
    try:
        if not text or not isinstance(text, str):
            return ""
            
        # Limpar texto básico mantendo pontuação importante
        text = re.sub(r'[^\w\s.,!?-]', ' ', text)  
        text = re.sub(r'\s+', ' ', text)           
        text = text.strip()                       
        
        # Limitar tamanho para modelos Transformers (512 tokens)
        words = text.split()
        if len(words) > 400:  # Margem de segurança
            text = ' '.join(words[:400])
        
        return text
    except Exception as e:
        logger.error(f"Error preprocessing text: {e}")
        return str(text) if text else ""

def classify_with_transformers(text):
    """Classificação híbrida usando Transformers"""
    try:
        if not classifier.sentiment_model:
            return classify_with_rules(text)
        
        # Preprocessar texto
        processed_text = preprocess_text(text)
        if not processed_text:
            return "Productive", 0.5, {}
        
        # Análise de sentimento
        sentiment_results = classifier.sentiment_model(processed_text)
        sentiment_scores = {result['label']: result['score'] for result in sentiment_results[0]}
        
        # Zero-shot classification (se disponível)
        zero_shot_result = None
        if classifier.zero_shot_classifier and len(processed_text) > 10:
            try:
                candidate_labels = [
                    "technical support request", 
                    "business inquiry", 
                    "complaint or issue",
                    "greeting or social message", 
                    "thank you message", 
                    "celebration or congratulations"
                ]
                zero_shot_result = classifier.zero_shot_classifier(processed_text, candidate_labels)
            except Exception as e:
                logger.warning(f"Zero-shot classification failed: {e}")
        
        # Extrair scores de sentimento
        negative_score = sentiment_scores.get('NEGATIVE', 0.0)
        positive_score = sentiment_scores.get('POSITIVE', 0.0)
        
        # Análise de palavras-chave para refinar classificação
        productive_keywords = [
            'help', 'issue', 'problem', 'error', 'bug', 'urgent', 'support', 
            'request', 'question', 'assistance', 'deadline', 'asap', 'fix',
            'troubleshoot', 'account', 'access', 'login', 'password', 'payment',
            'technical', 'system', 'application', 'website', 'service'
        ]
        
        nonproductive_keywords = [
            'thank', 'thanks', 'grateful', 'appreciate', 'congratulations',
            'birthday', 'holiday', 'vacation', 'celebrate', 'party', 'social',
            'greeting', 'hello', 'hi', 'good morning', 'good afternoon',
            'welcome', 'wishes', 'best regards'
        ]
        
        text_lower = text.lower()
        productive_matches = sum(1 for keyword in productive_keywords if keyword in text_lower)
        nonproductive_matches = sum(1 for keyword in nonproductive_keywords if keyword in text_lower)
        
        # Combinação inteligente de múltiplas fontes
        productive_score = 0.0
        nonproductive_score = 0.0
        
        # Sentimento (peso menor pois pode ser enganoso)
        productive_score += negative_score * 0.2  # Emails negativos tendem a ser produtivos
        nonproductive_score += positive_score * 0.3  # Emails positivos podem ser sociais
        
        # Palavras-chave (peso alto)
        productive_score += productive_matches * 0.3
        nonproductive_score += nonproductive_matches * 0.4
        
        # Zero-shot results (peso médio)
        if zero_shot_result:
            business_labels = ["technical support request", "business inquiry", "complaint or issue"]
            social_labels = ["greeting or social message", "thank you message", "celebration or congratulations"]
            
            top_label = zero_shot_result['labels'][0]
            top_score = zero_shot_result['scores'][0]
            
            if top_label in business_labels:
                productive_score += top_score * 0.4
            elif top_label in social_labels:
                nonproductive_score += top_score * 0.4
        
        # Ajustes baseados em estrutura do texto
        word_count = len(text.split())
        question_count = text.count('?')
        
        if question_count > 0:
            productive_score += 0.2
        
        if word_count < 30 and nonproductive_matches > 0:
            nonproductive_score += 0.3
        
        if word_count > 100:
            productive_score += 0.1
        
        # Decisão final
        if productive_score > nonproductive_score:
            classification = "Productive"
            confidence = min(0.95, 0.6 + productive_score)
        else:
            classification = "Non-Productive"
            confidence = min(0.95, 0.6 + nonproductive_score)
        
        # Preparar detalhes para resposta
        analysis_details = {
            'sentiment_scores': sentiment_scores,
            'productive_keywords_found': productive_matches,
            'nonproductive_keywords_found': nonproductive_matches,
            'zero_shot_top_label': zero_shot_result['labels'][0] if zero_shot_result else None,
            'zero_shot_confidence': zero_shot_result['scores'][0] if zero_shot_result else None
        }
        
        return classification, round(confidence, 2), analysis_details
        
    except Exception as e:
        logger.error(f"Transformers classification failed: {e}")
        return classify_with_rules(text)

def classify_with_rules(text):
    """Classificação de fallback baseada em regras simples"""
    try:
        productive_keywords = {
            'urgent', 'help', 'support', 'issue', 'problem', 'error', 'bug',
            'question', 'assistance', 'request', 'deadline', 'fix', 'repair',
            'technical', 'account', 'access', 'login', 'payment'
        }
        
        nonproductive_keywords = {
            'thank', 'thanks', 'appreciate', 'congratulations', 'birthday',
            'holiday', 'greeting', 'celebrate', 'party', 'social', 'welcome'
        }
        
        text_lower = text.lower()
        words = set(text_lower.split())
        
        productive_score = len(words.intersection(productive_keywords))
        nonproductive_score = len(words.intersection(nonproductive_keywords))
        
        word_count = len(text.split())
        question_count = text.count('?')
        
        # Ajustes heurísticos
        if question_count > 0:
            productive_score += 1
        if word_count > 50:
            productive_score += 1
        if word_count < 20 and nonproductive_score > 0:
            nonproductive_score += 2
        
        if productive_score > nonproductive_score:
            return "Productive", 0.75, {'method': 'rules', 'productive_matches': productive_score}
        else:
            return "Non-Productive", 0.65, {'method': 'rules', 'nonproductive_matches': nonproductive_score}
            
    except Exception as e:
        logger.error(f"Rule-based classification failed: {e}")
        return "Productive", 0.5, {'method': 'fallback'}

def generate_response(classification, confidence, original_text):
    """Gera resposta automática contextual"""
    
    if classification == "Productive":
        if confidence > 0.8:
            responses = [
                "Thank you for contacting us. We have received your request and understand its importance. Our technical team will review your issue and provide a detailed response within 24 hours.",
                "We appreciate you reaching out regarding this matter. Your inquiry has been assigned high priority and forwarded to our specialized support team. You can expect a comprehensive response within one business day.",
                "Thank you for bringing this to our attention. We recognize the urgency of your request and have escalated it to our senior technical staff. A team member will contact you shortly with a resolution."
            ]
        else:
            responses = [
                "Thank you for your email. We have received your message and will review it accordingly. Our team will get back to you within 48 hours.",
                "We appreciate your inquiry. Your message has been logged in our system and will be addressed by our support team within 2 business days.",
                "Thank you for contacting us. We have recorded your request and will ensure it receives appropriate attention from our team."
            ]
    else:
        responses = [
            "Thank you for your thoughtful message. We truly appreciate you taking the time to reach out and share your thoughts with us.",
            "We're grateful for your kind words and appreciate your continued engagement with our services. Thank you for being part of our community.",
            "Thank you for your email. It's always wonderful to hear from our valued clients, and we appreciate your ongoing relationship with us."
        ]
    
    # Selecionar resposta baseada no hash do texto para consistência
    response_index = hash(original_text) % len(responses)
    return responses[response_index]

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint com status detalhado"""
    models_status = {
        'sentiment_model': classifier.sentiment_model is not None,
        'zero_shot_classifier': classifier.zero_shot_classifier is not None,
        'device': str(classifier.device),
        'torch_version': torch.__version__,
        'cuda_available': torch.cuda.is_available()
    }
    
    response = jsonify({
        'status': 'healthy',
        'service': 'Transformers Email Classifier API',
        'version': '2.1.0',
        'ai_models': models_status,
        'features': [
            'PyTorch/Transformers classification',
            'Advanced sentiment analysis',
            'Zero-shot classification',
            'Hybrid ensemble system',
            'Robust fallback mechanisms'
        ]
    })
    
    # Headers CORS manuais para garantir compatibilidade
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/api/analyze', methods=['POST'])
def analyze_email():
    """Endpoint principal para análise de emails com Transformers"""
    logger.info("Transformers email analysis request received")
    
    try:
        email_text = ""
        
        # Processar input (texto ou arquivo)
        if 'text' in request.form and request.form['text'].strip():
            email_text = request.form['text'].strip()
            logger.info("Processing direct text input")
            
        elif 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                logger.info(f"Processing file: {filename}")
                
                if filename.lower().endswith('.txt'):
                    try:
                        email_text = file.read().decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            email_text = file.read().decode('latin1')
                        except:
                            email_text = file.read().decode('utf-8', errors='ignore')
                        
                elif filename.lower().endswith('.pdf'):
                    email_text = extract_text_from_pdf(file.stream)
            else:
                return jsonify({'error': 'Invalid file format. Please upload .txt or .pdf files only.'}), 400
        
        if not email_text or len(email_text.strip()) < 10:
            return jsonify({'error': 'Please provide email content with at least 10 characters.'}), 400
        
        # Classificação híbrida com Transformers
        classification, confidence, analysis_details = classify_with_transformers(email_text)
        logger.info(f"Classification: {classification}, Confidence: {confidence}")
        
        # Gerar resposta automática
        suggested_response = generate_response(classification, confidence, email_text)
        
        # Preprocessar para mostrar na resposta
        processed_text = preprocess_text(email_text)
        
        # Preparar resposta completa
        response_data = {
            'classification': classification,
            'confidence': confidence,
            'suggested_response': suggested_response,
            'original_text': email_text[:300] + "..." if len(email_text) > 300 else email_text,
            'processed_text': processed_text[:200] + "..." if len(processed_text) > 200 else processed_text,
            'ai_method': 'transformers_hybrid',
            'analysis_details': analysis_details,
            'analysis': {
                'text_length': len(email_text),
                'word_count': len(email_text.split()),
                'processed_words': len(processed_text.split()) if processed_text else 0,
                'question_marks': email_text.count('?'),
                'exclamation_marks': email_text.count('!'),
                'device_used': str(classifier.device)
            },
            'model_info': {
                'sentiment_model_loaded': classifier.sentiment_model is not None,
                'zero_shot_model_loaded': classifier.zero_shot_classifier is not None,
                'torch_version': torch.__version__
            }
        }
        
        logger.info("Analysis completed successfully")
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in email analysis: {error_msg}")
        return jsonify({'error': f'Internal server error: {error_msg}'}), 500

@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Retorna exemplos de emails para demonstração"""
    examples = {
        'productive': [
            "Hi, I'm experiencing a critical issue with my account login. The system keeps showing 'Authentication Failed' error even with correct credentials. This is urgent as I need to access my dashboard for an important client presentation today. Please help resolve this ASAP. Error code: AUTH_2023_FAILED",
            "Good morning, I need immediate assistance with a payment processing error. Transaction ID: TXN123456 failed but the amount was debited from my account. This is affecting our business operations and needs urgent attention from your technical team. The issue occurred at 2:30 PM yesterday.",
            "There seems to be a critical bug in your latest software update v2.1.5. The export function is not working properly and throwing a 500 internal server error. This is blocking our entire workflow and we need a fix or rollback procedure immediately. Our team of 15 people cannot proceed with their tasks."
        ],
        'non_productive': [
            "Thank you so much for the excellent customer service last month! Your team really went above and beyond to help us during the system migration process. We truly appreciate the dedication and professionalism shown by everyone involved. Looking forward to our continued partnership!",
            "Happy New Year to you and your entire team! Wishing everyone at your company a prosperous 2024 filled with success, growth, and innovation. Thank you for being such wonderful business partners throughout this past year. Here's to many more years of collaboration!",
            "Just wanted to express my heartfelt gratitude for the birthday wishes and the thoughtful gift card you sent. It really made my day special and showed how much you value our business relationship! Looking forward to continuing our great partnership in the coming months."
        ]
    }
    return jsonify(examples)

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Transformers-powered Flask app on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"PyTorch version: {torch.__version__}")
    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    logger.info(f"Models loaded: Sentiment={classifier.sentiment_model is not None}, Zero-shot={classifier.zero_shot_classifier is not None}")
    
    app.run(debug=debug, host='0.0.0.0', port=port)