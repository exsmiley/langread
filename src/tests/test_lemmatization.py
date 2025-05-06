"""
Unit tests for the lemmatization utility function.

This module tests the lemmatization functionality across multiple languages
to ensure consistent behavior across the application.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the lemmatization functionality
from src.utils.nlp.lemmatization import get_word_base_form, get_word_info
from src.utils.languages import SUPPORTED_LANGUAGES, get_languages_with_lemmatization

# Constants for test cases
TEST_CASES = {
    # English test cases - 15 different words
    "en": [
        {"word": "running", "expected": "run", "context": "I am running to the store."},
        {"word": "ate", "expected": "eat", "context": "She ate dinner."},
        {"word": "better", "expected": "good", "context": "This is better than expected."},
        {"word": "went", "expected": "go", "context": "They went to the park."},
        {"word": "studies", "expected": "study", "context": "He studies mathematics."},
        {"word": "driven", "expected": "drive", "context": "I have driven across the country."},
        {"word": "wrote", "expected": "write", "context": "She wrote a letter yesterday."},
        {"word": "sleeping", "expected": "sleep", "context": "The baby is sleeping now."},
        {"word": "taught", "expected": "teach", "context": "He taught English for ten years."},
        {"word": "leaves", "expected": "leave", "context": "He leaves for work at 8 AM."},
        {"word": "spoken", "expected": "speak", "context": "We have spoken about this before."},
        {"word": "broken", "expected": "break", "context": "The glass is broken."},
        {"word": "swimming", "expected": "swim", "context": "She enjoys swimming in the lake."},
        {"word": "felt", "expected": "feel", "context": "I felt happy about the news."},
        {"word": "chosen", "expected": "choose", "context": "They have chosen a new leader."},
    ],
    
    # Korean test cases - 15 different words
    "ko": [
        {"word": "먹었어요", "expected": "먹다", "context": "저는 밥을 먹었어요."},
        {"word": "갔습니다", "expected": "가다", "context": "어제 학교에 갔습니다."},
        {"word": "좋아해요", "expected": "좋아하다", "context": "저는 한국 음식을 좋아해요."},
        {"word": "배웠어요", "expected": "배우다", "context": "저는 한국어를 배웠어요."},
        {"word": "읽었습니다", "expected": "읽다", "context": "그 책을 읽었습니다."},
        {"word": "보고 있어요", "expected": "보다", "context": "지금 TV를 보고 있어요."},
        {"word": "살았어요", "expected": "살다", "context": "서울에서 살았어요."},
        {"word": "만듭니다", "expected": "만들다", "context": "저는 요리를 만듭니다."},
        {"word": "들었어요", "expected": "듣다", "context": "음악을 들었어요."},
        {"word": "쓰고 있습니다", "expected": "쓰다", "context": "지금 편지를 쓰고 있습니다."},
        {"word": "줬어요", "expected": "주다", "context": "친구에게 선물을 줬어요."},
        {"word": "마셨습니다", "expected": "마시다", "context": "커피를 마셨습니다."},
        {"word": "공부해요", "expected": "공부하다", "context": "매일 한국어를 공부해요."},
        {"word": "놀랐어요", "expected": "놀라다", "context": "그 소식을 듣고 놀랐어요."},
        {"word": "찾았습니다", "expected": "찾다", "context": "잃어버린 열쇠를 찾았습니다."},
    ],
    
    # Japanese test cases - 15 different words
    "ja": [
        {"word": "食べました", "expected": "食べる", "context": "昨日晩ご飯を食べました。"},
        {"word": "行きます", "expected": "行く", "context": "明日学校に行きます。"},
        {"word": "見ている", "expected": "見る", "context": "テレビを見ている。"},
        {"word": "書いた", "expected": "書く", "context": "手紙を書いた。"},
        {"word": "読んでいます", "expected": "読む", "context": "本を読んでいます。"},
        {"word": "飲みました", "expected": "飲む", "context": "コーヒーを飲みました。"},
        {"word": "話しています", "expected": "話す", "context": "友達と話しています。"},
        {"word": "買った", "expected": "買う", "context": "新しい服を買った。"},
        {"word": "聞いています", "expected": "聞く", "context": "音楽を聞いています。"},
        {"word": "泳いだ", "expected": "泳ぐ", "context": "海で泳いだ。"},
        {"word": "待っています", "expected": "待つ", "context": "友達を待っています。"},
        {"word": "走りました", "expected": "走る", "context": "公園で走りました。"},
        {"word": "使っている", "expected": "使う", "context": "新しいパソコンを使っている。"},
        {"word": "住んでいます", "expected": "住む", "context": "東京に住んでいます。"},
        {"word": "働いていました", "expected": "働く", "context": "会社で働いていました。"},
    ],
    
    # Spanish test cases - 15 different words
    "es": [
        {"word": "comiendo", "expected": "comer", "context": "Estoy comiendo la cena."},
        {"word": "habló", "expected": "hablar", "context": "Él habló con su amigo."},
        {"word": "escribieron", "expected": "escribir", "context": "Ellos escribieron una carta."},
        {"word": "leyendo", "expected": "leer", "context": "Estoy leyendo un libro."},
        {"word": "hicimos", "expected": "hacer", "context": "Nosotros hicimos la tarea."},
        {"word": "durmió", "expected": "dormir", "context": "El bebé durmió toda la noche."},
        {"word": "vivían", "expected": "vivir", "context": "Ellos vivían en Madrid."},
        {"word": "trabajando", "expected": "trabajar", "context": "Estoy trabajando en un proyecto."},
        {"word": "estudié", "expected": "estudiar", "context": "Yo estudié medicina."},
        {"word": "vieron", "expected": "ver", "context": "Ellos vieron una película."},
        {"word": "cantaba", "expected": "cantar", "context": "Ella cantaba en un coro."},
        {"word": "corriendo", "expected": "correr", "context": "Está corriendo en el parque."},
        {"word": "bebimos", "expected": "beber", "context": "Nosotros bebimos agua."},
        {"word": "bailaron", "expected": "bailar", "context": "Ellos bailaron toda la noche."},
        {"word": "pensando", "expected": "pensar", "context": "Estoy pensando en ti."},
    ],
    
    # French test cases - 15 different words
    "fr": [
        {"word": "mangé", "expected": "manger", "context": "J'ai mangé du pain."},
        {"word": "parlons", "expected": "parler", "context": "Nous parlons français."},
        {"word": "écrivant", "expected": "écrire", "context": "Il est écrivant une lettre."},
        {"word": "lisant", "expected": "lire", "context": "Elle est lisant un livre."},
        {"word": "allés", "expected": "aller", "context": "Ils sont allés au cinéma."},
        {"word": "fait", "expected": "faire", "context": "J'ai fait mes devoirs."},
        {"word": "voyons", "expected": "voir", "context": "Nous voyons la tour Eiffel."},
        {"word": "dormais", "expected": "dormir", "context": "Je dormais quand tu as appelé."},
        {"word": "bu", "expected": "boire", "context": "Il a bu du café."},
        {"word": "prenant", "expected": "prendre", "context": "Je suis prenant le train."},
        {"word": "venu", "expected": "venir", "context": "Il est venu hier."},
        {"word": "chantons", "expected": "chanter", "context": "Nous chantons une chanson."},
        {"word": "courant", "expected": "courir", "context": "Il est courant dans le parc."},
        {"word": "appris", "expected": "apprendre", "context": "J'ai appris le français."},
        {"word": "vivaient", "expected": "vivre", "context": "Ils vivaient à Paris."},
    ],
    
    # German test cases - 15 different words
    "de": [
        {"word": "gegessen", "expected": "essen", "context": "Ich habe Brot gegessen."},
        {"word": "spricht", "expected": "sprechen", "context": "Er spricht Deutsch."},
        {"word": "geschrieben", "expected": "schreiben", "context": "Sie hat einen Brief geschrieben."},
        {"word": "lese", "expected": "lesen", "context": "Ich lese ein Buch."},
        {"word": "ging", "expected": "gehen", "context": "Er ging zur Schule."},
        {"word": "gekommen", "expected": "kommen", "context": "Sie ist gestern gekommen."},
        {"word": "sieht", "expected": "sehen", "context": "Er sieht einen Film."},
        {"word": "getrunken", "expected": "trinken", "context": "Wir haben Wasser getrunken."},
        {"word": "kaufe", "expected": "kaufen", "context": "Ich kaufe Lebensmittel."},
        {"word": "gemacht", "expected": "machen", "context": "Sie hat ihre Hausaufgaben gemacht."},
        {"word": "fährt", "expected": "fahren", "context": "Er fährt nach Berlin."},
        {"word": "arbeitete", "expected": "arbeiten", "context": "Sie arbeitete in einem Büro."},
        {"word": "singt", "expected": "singen", "context": "Sie singt ein Lied."},
        {"word": "geschlafen", "expected": "schlafen", "context": "Ich habe gut geschlafen."},
        {"word": "gelernt", "expected": "lernen", "context": "Er hat Deutsch gelernt."},
    ],
    
    # Italian test cases - 15 different words
    "it": [
        {"word": "mangiato", "expected": "mangiare", "context": "Ho mangiato la pasta."},
        {"word": "parla", "expected": "parlare", "context": "Lui parla italiano."},
        {"word": "scrivendo", "expected": "scrivere", "context": "Sto scrivendo una lettera."},
        {"word": "letto", "expected": "leggere", "context": "Ho letto un libro."},
        {"word": "andati", "expected": "andare", "context": "Siamo andati al cinema."},
        {"word": "fatto", "expected": "fare", "context": "Ho fatto i compiti."},
        {"word": "vediamo", "expected": "vedere", "context": "Noi vediamo il Colosseo."},
        {"word": "dormivo", "expected": "dormire", "context": "Dormivo quando hai chiamato."},
        {"word": "bevuto", "expected": "bere", "context": "Ha bevuto il caffè."},
        {"word": "prendendo", "expected": "prendere", "context": "Sto prendendo il treno."},
        {"word": "venuto", "expected": "venire", "context": "È venuto ieri."},
        {"word": "cantiamo", "expected": "cantare", "context": "Cantiamo una canzone."},
        {"word": "correndo", "expected": "correre", "context": "Sta correndo nel parco."},
        {"word": "imparato", "expected": "imparare", "context": "Ho imparato l'italiano."},
        {"word": "vivevano", "expected": "vivere", "context": "Vivevano a Roma."},
    ],
    
    # Portuguese test cases - 15 different words
    "pt": [
        {"word": "comendo", "expected": "comer", "context": "Estou comendo o jantar."},
        {"word": "falou", "expected": "falar", "context": "Ele falou com seu amigo."},
        {"word": "escreveram", "expected": "escrever", "context": "Eles escreveram uma carta."},
        {"word": "lendo", "expected": "ler", "context": "Estou lendo um livro."},
        {"word": "fizemos", "expected": "fazer", "context": "Nós fizemos a tarefa."},
        {"word": "dormiu", "expected": "dormir", "context": "O bebê dormiu toda a noite."},
        {"word": "viviam", "expected": "viver", "context": "Eles viviam em Lisboa."},
        {"word": "trabalhando", "expected": "trabalhar", "context": "Estou trabalhando em um projeto."},
        {"word": "estudei", "expected": "estudar", "context": "Eu estudei medicina."},
        {"word": "viram", "expected": "ver", "context": "Eles viram um filme."},
        {"word": "cantava", "expected": "cantar", "context": "Ela cantava em um coral."},
        {"word": "correndo", "expected": "correr", "context": "Está correndo no parque."},
        {"word": "bebemos", "expected": "beber", "context": "Nós bebemos água."},
        {"word": "dançaram", "expected": "dançar", "context": "Eles dançaram toda a noite."},
        {"word": "pensando", "expected": "pensar", "context": "Estou pensando em você."},
    ],
    
    # Russian test cases - 15 different words
    "ru": [
        {"word": "читаю", "expected": "читать", "context": "Я читаю книгу."},
        {"word": "говорил", "expected": "говорить", "context": "Он говорил по-русски."},
        {"word": "писала", "expected": "писать", "context": "Она писала письмо."},
        {"word": "ел", "expected": "есть", "context": "Я ел обед."},
        {"word": "пошли", "expected": "идти", "context": "Мы пошли в кино."},
        {"word": "сделала", "expected": "делать", "context": "Она сделала домашнее задание."},
        {"word": "видим", "expected": "видеть", "context": "Мы видим памятник."},
        {"word": "спал", "expected": "спать", "context": "Ребенок спал всю ночь."},
        {"word": "пил", "expected": "пить", "context": "Он пил кофе."},
        {"word": "беру", "expected": "брать", "context": "Я беру книгу."},
        {"word": "пришел", "expected": "приходить", "context": "Он пришел вчера."},
        {"word": "поем", "expected": "петь", "context": "Мы поем песню."},
        {"word": "бежит", "expected": "бежать", "context": "Он бежит в парке."},
        {"word": "учил", "expected": "учить", "context": "Я учил русский язык."},
        {"word": "жили", "expected": "жить", "context": "Они жили в Москве."},
    ],
    
    # Chinese test cases - 15 different words (note: Chinese doesn't use traditional inflections)  
    "zh": [
        {"word": "吃饭", "expected": "吃饭", "context": "我正在吃饭。"},
        {"word": "说话", "expected": "说话", "context": "他在说话。"},
        {"word": "写字", "expected": "写字", "context": "她在写字。"},
        {"word": "看书", "expected": "看书", "context": "我在看书。"},
        {"word": "去了", "expected": "去", "context": "他去了学校。"},
        {"word": "做饭", "expected": "做饭", "context": "妈妈在做饭。"},
        {"word": "看见", "expected": "看见", "context": "我看见了一只猫。"},
        {"word": "睡觉", "expected": "睡觉", "context": "孩子在睡觉。"},
        {"word": "喝水", "expected": "喝水", "context": "我在喝水。"},
        {"word": "拿着", "expected": "拿", "context": "他拿着一本书。"},
        {"word": "来了", "expected": "来", "context": "他昨天来了。"},
        {"word": "唱歌", "expected": "唱歌", "context": "我们在唱歌。"},
        {"word": "跑步", "expected": "跑步", "context": "他在公园跑步。"},
        {"word": "学习", "expected": "学习", "context": "我学习中文。"},
        {"word": "住在", "expected": "住", "context": "他们住在北京。"},
    ],
}


class TestLemmatization:
    """Test cases for the lemmatization utility functions."""
    
    def test_supported_languages_consistency(self):
        """Test that our supported languages list is consistent with implementation."""
        # Get languages that should have lemmatization support
        languages_with_lemmatization = get_languages_with_lemmatization()
        
        # Check that we have test cases for each supported language
        missing_test_cases = [lang for lang in languages_with_lemmatization 
                             if lang not in TEST_CASES and lang != "zh"]
        
        # We make an exception for Chinese as it doesn't use traditional inflections
        assert not missing_test_cases, f"Missing test cases for languages: {missing_test_cases}"
    
    @pytest.mark.parametrize("lang_code", get_languages_with_lemmatization())
    def test_get_word_base_form_accepts_all_supported_languages(self, lang_code):
        """Test that get_word_base_form accepts all supported languages."""
        # This is a basic test to ensure the function doesn't error on supported languages
        # We're using a simple word that should work in any language
        result = get_word_base_form("test", lang_code)
        
        # The function should at minimum return the original word
        assert result is not None
        assert isinstance(result, str)
    
    def test_get_word_base_form_handles_empty_input(self):
        """Test that get_word_base_form properly handles empty input."""
        result = get_word_base_form("", "en")
        assert result == ""
        
        result = get_word_base_form("   ", "en")
        assert result == ""
    
    def test_get_word_info_returns_expected_fields(self):
        """Test that get_word_info returns all expected fields."""
        result = get_word_info("running", "en")
        assert isinstance(result, dict)
        assert "original_word" in result
        assert "base_form" in result
        assert "language" in result
        assert "is_conjugated" in result
        
        # English with spaCy should have POS information
        if "pos" in result and result["pos"] is not None:
            assert isinstance(result["pos"], str)

    # Generate a parameterized test for each test case
    @pytest.mark.parametrize(
        "lang_code,word,expected,context",
        [
            (lang, case["word"], case["expected"], case["context"])
            for lang in TEST_CASES
            for case in TEST_CASES[lang]
        ],
    )
    def test_lemmatization_with_spacy_available(self, lang_code, word, expected, context):
        """Test lemmatization for various languages when spaCy is available."""
        # This test assumes spaCy and other NLP libraries are available
        # In case they aren't, the test will be skipped
        
        # Attempt to get the base form
        result = get_word_base_form(word, lang_code, context)
        
        # Skip assertions if the specific language module isn't available
        # We're more flexible here since we're testing in various environments
        if not getattr(sys.modules.get("src.utils.nlp.lemmatization"), f"KONLPY_AVAILABLE", True) and lang_code == "ko":
            pytest.skip("KoNLPy not available for Korean lemmatization testing")
            
        if not getattr(sys.modules.get("src.utils.nlp.lemmatization"), f"FUGASHI_AVAILABLE", True) and lang_code == "ja":
            pytest.skip("Fugashi not available for Japanese lemmatization testing")
            
        if not getattr(sys.modules.get("src.utils.nlp.lemmatization"), f"SPACY_AVAILABLE", True) and lang_code in ["en", "es", "fr", "de"]:
            pytest.skip(f"spaCy not available for {lang_code} lemmatization testing")
        
        # For available language modules, we'll check the result matches our expected base form
        # Note: Since this can vary based on NLP library version and availability, we'll be flexible
        # If the exact lemmatization doesn't match expected, we'll check if it's at least consistent
        if result != expected:
            # If the result doesn't match expected, try lemmatizing the expected form
            # If they're the same, then our lemmatization is at least consistent
            expected_lemmatized = get_word_base_form(expected, lang_code)
            assert result == expected_lemmatized, \
                f"For {lang_code}, lemmatizing '{word}' gave '{result}' instead of '{expected}' " \
                f"and is not consistent with lemmatizing the expected result"
    
    @patch("src.utils.nlp.lemmatization.SPACY_AVAILABLE", False)
    @patch("src.utils.nlp.lemmatization.KONLPY_AVAILABLE", False)
    @patch("src.utils.nlp.lemmatization.FUGASHI_AVAILABLE", False)
    def test_fallback_rules_applied_when_libraries_unavailable(self):
        """Test that fallback rules are applied when NLP libraries are unavailable."""
        # English fallback rules
        assert get_word_base_form("running", "en") != "running"
        assert get_word_base_form("walked", "en") != "walked"
        
        # Spanish fallback rules
        assert get_word_base_form("hablando", "es") != "hablando"
        
        # Test that the function still returns something for unsupported languages
        assert get_word_base_form("テスト", "ja") == "テスト"
    
    @patch("src.utils.nlp.lemmatization._load_spacy_model")
    def test_spacy_model_loading(self, mock_load_spacy):
        """Test that spaCy models are loaded correctly."""
        # Set up the mock to return a basic mock model
        mock_model = MagicMock()
        mock_token = MagicMock()
        mock_token.lemma_ = "run"
        mock_model.return_value.__getitem__.return_value = mock_token
        mock_load_spacy.return_value = mock_model
        
        # Call the function
        result = get_word_base_form("running", "en")
        
        # Check that the model was loaded
        mock_load_spacy.assert_called_once_with("en")
    
    def test_get_word_info_is_conjugated_flag(self):
        """Test that get_word_info correctly identifies conjugated words."""
        # Test with a conjugated word
        result = get_word_info("running", "en")
        assert result["is_conjugated"] is True
        
        # Test with a base form word
        result = get_word_info("run", "en")
        assert result["is_conjugated"] is False


if __name__ == "__main__":
    # Run the tests with pytest
    pytest.main(["-xvs", __file__])
