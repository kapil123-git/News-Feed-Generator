from nltk.stem.porter import *
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import defaultdict
from collections import Counter


class Document(object):

    stop_words = stopwords.words('english')
    
    def __init__(self, f_path, topic=None):
        
        self.content = open(f_path, 'r',errors='ignore').readlines()
        self.img = self.content[0]
        try:
            self.title = self.content[1]
        except:
            self.title = "Not avaiable"
        self.text = ' '.join(self.content[2:])
        self.topic = topic

        """
        # No stemmer or lemmatizer.
        self.title_tokens = self.tokenize(self.title)
        self.text_tokens = self.tokenize(self.text)

        # Only stemmer.
        self.title_tokens = self.stem(self.tokenize(self.title))
        self.text_tokens = self.stem(self.tokenize(self.text))

        """
        # Only lemmatizer.
        self.title_tokens = self.lemmatize(self.tokenize(self.title))
        self.text_tokens = self.lemmatize(self.tokenize(self.text))
        """

        # Both stemmer and lemmatizer.
        self.title_tokens = self.stem(self.lemmatize(self.tokenize(self.title)))
        self.text_tokens = self.stem(self.lemmatize(self.tokenize(self.text)))
        """

        self.tf = self.tf_index(self.text_tokens)

        self.tfidf = None
        self.tfidfie = None
        self.vector = None
        self.term_count()
    
    def document_terms(self):

        return self.terms
    
    def term_count(self):
        
        self.terms = Counter()
        
        for token in self.title_tokens:
            self.terms[token] += 1
            # ek file mai kitne tyms vo word aya hai
        for token in self.text_tokens:
            self.terms[token] += 1
            # ek file mai kitne tyms vo word aya hai
            
    def tokenize(self, data):
        # return [t.lower() for t in re.findall(r"\w+(?:[-']\w+)*", data) if t not in self.stop_words]
        return [t.lower() for t in re.findall(r"\w+(?:[-']\w+)*", data) if t not in self.stop_words and len(t) > 2]
        # jo stopwords nhi hai and len 2 se jyada hai usko lower case mai convert karke return karo

    def stem(self, tokens):

        stemmer = PorterStemmer()

        return [stemmer.stem(token) for token in tokens]

    def lemmatize(self, tokens):

        lemmatizer = WordNetLemmatizer()
        #agree agree wala roma exmp kaise pata chala wordnet database dekhke

        return [lemmatizer.lemmatize(token) for token in tokens]

    def tf_index(self, token_list):

        tf = defaultdict(lambda: 0)
        for token in token_list:
            tf[token] = tf[token] + 1
        
        # ek document mai ek word ka percentage
        return tf