from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import PyPDF2
import io
import re
import logging
from dotenv import load_dotenv
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

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

# Classificador leve baseado em regras e análise de texto
class LightweightClassifier:
    def __init__(self):
        self.textblob_available = TEXTBLOB_AVAILABLE
        logger.info(f"Initializing lightweight classifier")
        logger.info(f"TextBlob available: {self.textblob_available}")
        
        # Palavras-chave categorizadas para classificação
        self.productive_keywords = {
            'urgent', 'help', 'support', 'issue', 'problem', 'error', 'bug',
            'question', 'assistance', 'request', 'deadline', 'fix', 'repair',
            'technical', 'account', 'access', 'login', 'password', 'payment',
            'troubleshoot', 'system', 'application', 'website', 'service',
            'broken', 'not working', 'failing', 'crash', 'stuck', 'blocked',
            'asap', 'immediately', 'priority', 'critical', 'emergency'
        }
        
        self.nonproductive_keywords = {
            'thank', 'thanks', 'grateful', 'appreciate', 'congratulations',
            'birthday', 'holiday', 'vacation', 'celebrate', 'party', 'social',
            'greeting', 'hello', 'hi', 'good morning', 'good afternoon',
            'welcome', 'wishes', 'best regards', 'cheers', 'love', 'miss you',
            'hope you are well', 'how are you', 'long time no see', 'catch up'
        }
        
        # Padrões de email produtivos
        self.productive_patterns = [
            r'\b(error|bug|issue)\s+(#?\w+)',  # Error codes
            r'(can\'?t|cannot|unable to)\s+\w+',  # Cannot do something
            r'\b(fix|resolve|solve|repair)\b',  # Action requests
            r'\?\s*$',  # Questions
            r'deadline\s+\w+',  # Deadlines
            r'urgent|asap|immediately',  # Urgency
        ]
        
        logger.info("Lightweight classifier initialized successfully")

# Instância global do classificador
classifier = LightweightClassifier()

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

def classify_with_lightweight_ai(text):
    """Classificação leve usando TextBlob + regras avançadas"""
    try:
        processed_text = preprocess_text(text)
        if not processed_text:
            return "Productive", 0.5, {'method': 'empty_text'}
        
        text_lower = text.lower()
        analysis_details = {}
        
        # 1. Análise de sentimento com TextBlob (se disponível)
        sentiment_score = 0.0
        if classifier.textblob_available:
            try:
                blob = TextBlob(processed_text)
                sentiment_score = blob.sentiment.polarity  # -1 to 1
                subjectivity = blob.sentiment.subjectivity  # 0 to 1
                analysis_details['sentiment_polarity'] = round(sentiment_score, 3)
                analysis_details['subjectivity'] = round(subjectivity, 3)
            except Exception as e:
                logger.warning(f"TextBlob analysis failed: {e}")
        
        # 2. Contagem de palavras-chave
        productive_matches = sum(1 for keyword in classifier.productive_keywords if keyword in text_lower)
        nonproductive_matches = sum(1 for keyword in classifier.nonproductive_keywords if keyword in text_lower)
        
        # 3. Análise de padrões usando regex
        pattern_matches = 0
        for pattern in classifier.productive_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                pattern_matches += 1
        
        # 4. Análise estrutural do texto
        word_count = len(text.split())
        sentence_count = len([s for s in text.split('.') if s.strip()])
        question_count = text.count('?')
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        
        analysis_details.update({
            'productive_keywords': productive_matches,
            'nonproductive_keywords': nonproductive_matches,
            'pattern_matches': pattern_matches,
            'word_count': word_count,
            'question_count': question_count,
            'exclamation_count': exclamation_count,
            'caps_ratio': round(caps_ratio, 3)
        })
        
        # 5. Cálculo de score de produtividade
        productive_score = 0.0
        
        # Palavras-chave produtivas (peso alto)
        productive_score += productive_matches * 0.3
        
        # Padrões produtivos (peso médio)
        productive_score += pattern_matches * 0.2
        
        # Perguntas indicam necessidade de resposta
        productive_score += question_count * 0.15
        
        # Texto longo pode indicar problema complexo
        if word_count > 50:
            productive_score += 0.1
        if word_count > 100:
            productive_score += 0.1
        
        # Muitas maiúsculas podem indicar urgência
        if caps_ratio > 0.1:
            productive_score += 0.1
        
        # Sentimento negativo pode indicar problema
        if sentiment_score < -0.2:
            productive_score += 0.15
        
        # Score de não-produtividade
        nonproductive_score = 0.0
        
        # Palavras-chave não-produtivas (peso alto)
        nonproductive_score += nonproductive_matches * 0.4
        
        # Sentimento muito positivo pode ser social
        if sentiment_score > 0.3:
            nonproductive_score += 0.2
        
        # Mensagens muito curtas com agradecimentos
        if word_count < 30 and nonproductive_matches > 0:
            nonproductive_score += 0.3
        
        # Baixa subjetividade com palavras positivas
        if classifier.textblob_available and 'subjectivity' in analysis_details:
            if analysis_details['subjectivity'] < 0.3 and nonproductive_matches > 0:
                nonproductive_score += 0.2
        
        # 6. Decisão final
        if productive_score > nonproductive_score:
            classification = "Productive"
            confidence = min(0.95, 0.6 + (productive_score * 0.8))
        else:
            classification = "Non-Productive"  
            confidence = min(0.95, 0.6 + (nonproductive_score * 0.8))
        
        # Ajustar confiança baseada na diferença de scores
        score_diff = abs(productive_score - nonproductive_score)
        if score_diff > 0.5:
            confidence = min(0.95, confidence + 0.1)
        
        analysis_details.update({
            'productive_score': round(productive_score, 3),
            'nonproductive_score': round(nonproductive_score, 3),
            'score_difference': round(score_diff, 3),
            'method': 'lightweight_ai'
        })
        
        return classification, round(confidence, 2), analysis_details
        
    except Exception as e:
        logger.error(f"Lightweight AI classification failed: {e}")
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
        'textblob_available': classifier.textblob_available,
        'classification_method': 'lightweight_ai',
        'productive_keywords': len(classifier.productive_keywords),
        'nonproductive_keywords': len(classifier.nonproductive_keywords),
        'patterns_count': len(classifier.productive_patterns)
    }
    
    response = jsonify({
        'status': 'healthy',
        'service': 'Lightweight Email Classifier API',
        'version': '3.0.0',
        'ai_models': models_status,
        'features': [
            'Lightweight text classification',
            'TextBlob sentiment analysis',
            'Pattern-based recognition',
            'Rule-based classification',
            'Fast and memory-efficient'
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
        
        # Classificação leve com TextBlob + regras
        classification, confidence, analysis_details = classify_with_lightweight_ai(email_text)
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
            'ai_method': 'lightweight_hybrid',
            'analysis_details': analysis_details,
            'analysis': {
                'text_length': len(email_text),
                'word_count': len(email_text.split()),
                'processed_words': len(processed_text.split()) if processed_text else 0,
                'question_marks': email_text.count('?'),
                'exclamation_marks': email_text.count('!'),
                'memory_efficient': True
            },
            'model_info': {
                'textblob_available': classifier.textblob_available,
                'classification_method': 'rule_based_with_sentiment',
                'lightweight_version': '3.0.0'
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
    
    logger.info(f"Starting Lightweight Email Classifier Flask app on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"TextBlob available: {classifier.textblob_available}")
    logger.info(f"Classification method: Lightweight AI + Rules")
    logger.info(f"Memory usage: Minimal (< 50MB)")
    
    app.run(debug=debug, host='0.0.0.0', port=port)