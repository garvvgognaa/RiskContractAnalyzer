import re
from typing import List

def segment_into_clauses(text: str) -> List[str]:
           
    if not text:
        return []

                                                       
                                                           
    paragraphs = re.split(r'\n\s*\n', text)
    
    clauses = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
                                                                                                            
                                                                                                   
                                     
                                                                           
        
                                                                                                           
        delimiters = r'(?m)(^\s*\d+\.\d*\s*|^\s*[a-z]\)\s*|^\s*[ivx]+\.\s*)'
        
                                                 
        parts = re.split(delimiters, para)
        
                                 
        current_clause = ""
        for i, part in enumerate(parts):
            if re.match(delimiters, part):
                                                                                  
                if current_clause:
                    clauses.append(current_clause.strip())
                current_clause = part                                      
            else:
                current_clause += part
                
        if current_clause:
            clauses.append(current_clause.strip())

                                                                    
    final_clauses = [c for c in clauses if len(c.split()) > 3]
    
    return final_clauses
