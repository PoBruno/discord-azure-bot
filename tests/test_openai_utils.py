import unittest
from src.openai_utils import generate_response

class TestOpenAIUtils(unittest.TestCase):
    def test_generate_response(self):
        # Teste simples verificando se a função retorna uma string
        prompt = "Hello, how are you?"
        response = generate_response(prompt)
        self.assertIsInstance(response, str)

if __name__ == '__main__':
    unittest.main()