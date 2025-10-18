from db_access import VectorDB
from embedder import Embedder
from interact_llamacpp import LLM
import sys

MODEL_PATH = 'model-q4_K.gguf'

embedder = Embedder()
vectors = VectorDB()
llm = LLM()

print('Инициализировано')
if '-llm' in sys.argv:
    llm.initialize(MODEL_PATH, system_prompt='Ты - ассистент компании Транснефть. Твоя задача - отвечать на вопросы пользователей, пользуясь **только** информацией, которую тебе предоставил пользователь. Ты НЕ отвечаешь на вопросы, не связанные с Транснефтью. Ты НЕ используешь факты, не предложенные тебе. Если ты не можешь ответить на вопрос, пользуясь только данной тебе информацией, отвечай, что ты не знаешь и это не по теме.')
    vectors.load('llm.bin', 'llm_dcts.bin')
    print('Режим LLM')
    while True:
        try:
            message = input('Введите сообщение: ')
            info = vectors.search(embedder.embed(message))[2][0]["context"]
            print(info)
            print(llm.interact(info + message))
        except KeyboardInterrupt:
            break
else:
    vectors.load('questions.bin', 'questions_dcts.bin')
    while True:
        try:
            message = input('Введите сообщение: ')
            print(vectors.search(embedder.embed(message)))
        except KeyboardInterrupt:
            break