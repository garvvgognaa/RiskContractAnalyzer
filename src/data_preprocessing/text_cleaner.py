import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

                      
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
                                                                 
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

def clean_text(text: str) -> str:
           
    if not text:
        return ""
    
                        
    text = text.lower()
    
                                                                              
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
                       
    tokens = word_tokenize(text)
    
                      
    stop_words = set(stopwords.words('english'))
    cleaned_tokens = [word for word in tokens if word not in stop_words]
    
                                           
    cleaned_text = ' '.join(cleaned_tokens)
    
                                            
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text
