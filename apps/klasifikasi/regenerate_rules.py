import re
import random
import logging

logger = logging.getLogger(__name__)

class SmartRegeneratorRules:
    """
    Sistem regenerasi berbasis aturan (Rule-based) untuk Bloom's Taxonomy.
    Mengekstrak topik dari soal lama dan memasukkannya ke template level baru.
    """

    def __init__(self):
        # Pola untuk membersihkan pertanyaan lama agar mendapatkan "Topik Inti"
        # Contoh: "Jelaskan apa itu Database" -> Topik: "Database"
        self.CLEANING_PATTERNS_ID = [
            r'^(?:jelaskan|sebutkan|uraikan|apa\s+itu|bagaimana|mengapa|analisis|evaluasi|buatlah|rancanglah)\s+(?:tentang|mengenai|yang\s+dimaksud\s+dengan)?',
            r'^apakah\s+yang\s+dimaksud\s+(?:dengan)?',
            r'^definisi\s+(?:dari)?',
            r'\?+$', # Hapus tanda tanya di akhir
            r'\.$'   # Hapus titik di akhir
        ]

        self.CLEANING_PATTERNS_EN = [
            r'^(?:explain|define|list|describe|analyze|evaluate|create|design|what\s+is|how\s+does|why\s+does)\s+(?:the\s+concept\s+of|the|a|an)?',
            r'^what\s+do\s+you\s+mean\s+by',
            r'\?+$',
            r'\.$'
        ]

        # Template Bloom's Taxonomy (Indonesian)
        self.TEMPLATES_ID = {
            'C1': [ # Remember
                "Definisikan apa yang dimaksud dengan {topic}.",
                "Sebutkan karakteristik utama dari {topic}.",
                "Apa pengertian dari {topic}?",
                "Identifikasi elemen-elemen dasar pada {topic}."
            ],
            'C2': [ # Understand
                "Jelaskan prinsip kerja {topic} dengan kata-kata Anda sendiri.",
                "Uraikan perbedaan utama dalam konsep {topic}.",
                "Ringkaslah tujuan utama dari {topic}.",
                "Berikan contoh nyata untuk menjelaskan {topic}."
            ],
            'C3': [ # Apply
                "Bagaimana Anda akan menerapkan {topic} dalam studi kasus perusahaan nyata?",
                "Demonstrasikan penggunaan {topic} untuk menyelesaikan masalah data.",
                "Hitunglah atau tentukan hasil jika {topic} diterapkan pada skenario standar.",
                "Berikan contoh implementasi {topic} pada sistem informasi modern."
            ],
            'C4': [ # Analyze
                "Analisis faktor-faktor penyebab kegagalan atau keberhasilan dalam {topic}.",
                "Bandingkan kelebihan dan kekurangan dari {topic} dengan pendekatan lain.",
                "Klasifikasikan komponen-komponen penyusun {topic} dan jelaskan hubungannya.",
                "Identifikasi pola atau anomali yang mungkin terjadi pada {topic}."
            ],
            'C5': [ # Evaluate
                "Evaluasi efektivitas penggunaan {topic} dalam jangka panjang.",
                "Kritisi kelemahan dari {topic} dan berikan argumen Anda.",
                "Apakah {topic} merupakan solusi terbaik? Berikan justifikasi penilaian Anda.",
                "Nilailah dampak risiko keamanan jika menggunakan {topic}."
            ],
            'C6': [ # Create
                "Rancanglah sebuah kerangka kerja baru yang mengoptimalkan {topic}.",
                "Buatlah proposal strategi untuk mengembangkan {topic} menjadi lebih efisien.",
                "Desainlah diagram alur sistem yang mengintegrasikan {topic}.",
                "Ciptakan solusi alternatif inovatif berbasis {topic}."
            ]
        }

        # Template Bloom's Taxonomy (English)
        self.TEMPLATES_EN = {
            'C1': [ # Remember
                "Define exactly what is meant by {topic}.",
                "List the primary characteristics of {topic}.",
                "What is the formal definition of {topic}?",
                "Identify the basic elements of {topic}."
            ],
            'C2': [ # Understand
                "Explain the working principle of {topic} in your own words.",
                "Describe the main differences within the concept of {topic}.",
                "Summarize the primary purpose of {topic}.",
                "Provide a real-world example to illustrate {topic}."
            ],
            'C3': [ # Apply
                "How would you apply {topic} in a real corporate case study?",
                "Demonstrate the use of {topic} to solve a specific data problem.",
                "Calculate or determine the outcome if {topic} is applied to a standard scenario.",
                "Illustrate the implementation of {topic} in modern information systems."
            ],
            'C4': [ # Analyze
                "Analyze the factors contributing to the success or failure of {topic}.",
                "Compare and contrast the pros and cons of {topic} versus alternatives.",
                "Classify the components of {topic} and explain their relationships.",
                "Identify potential patterns or anomalies within {topic}."
            ],
            'C5': [ # Evaluate
                "Evaluate the long-term effectiveness of using {topic}.",
                "Critique the potential weaknesses of {topic} and support your argument.",
                "Justify whether {topic} is the best solution for high-scale systems.",
                "Assess the security risks associated with {topic}."
            ],
            'C6': [ # Create
                "Design a new framework that optimizes {topic}.",
                "Formulate a strategic proposal to enhance {topic}.",
                "Create a system flowchart that integrates {topic}.",
                "Develop an innovative alternative solution based on {topic}."
            ]
        }

    def detect_language(self, text):
        """Simple language detection based on stopwords"""
        text_lower = text.lower()
        id_score = sum(1 for w in ['yang', 'dan', 'dari', 'apa', 'bagaimana', 'adalah'] if w in text_lower)
        en_score = sum(1 for w in ['the', 'and', 'of', 'what', 'how', 'is'] if w in text_lower)
        return 'id' if id_score >= en_score else 'en'

    def extract_topic(self, question, lang):
        """
        Membersihkan pertanyaan untuk mendapatkan topik inti.
        """
        clean_text = question.strip()
        patterns = self.CLEANING_PATTERNS_ID if lang == 'id' else self.CLEANING_PATTERNS_EN
        
        for pattern in patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE).strip()
        
        # Capitalize first letter logic
        if clean_text:
            clean_text = clean_text[0].upper() + clean_text[1:]
            
        return clean_text

    def generate_question(self, original_question, target_level):
        """
        Fungsi utama untuk meregenerate pertanyaan.
        """
        try:
            # 1. Detect Language
            lang = self.detect_language(original_question)
            
            # 2. Extract Topic
            topic = self.extract_topic(original_question, lang)
            
            # Jika topik terlalu pendek (gagal ekstrak), kembalikan None agar fallback ke AI
            if len(topic) < 3: 
                logger.warning(f"Topic extraction failed/too short for: {original_question}")
                return None

            # 3. Select Template
            templates = self.TEMPLATES_ID if lang == 'id' else self.TEMPLATES_EN
            
            # Validasi level
            if target_level not in templates:
                return None

            # Pilih template secara acak
            template = random.choice(templates[target_level])
            
            # 4. Construct New Question
            new_question = template.format(topic=topic)
            
            return new_question

        except Exception as e:
            logger.error(f"Error in SmartRegeneratorRules: {str(e)}")
            return None

# Singleton instance
smart_regenerator = SmartRegeneratorRules()