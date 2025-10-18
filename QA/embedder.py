import torch.nn.functional as F
import torch
from torch import Tensor
from transformers import AutoTokenizer, AutoModel

class Embedder:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('intfloat/multilingual-e5-small')
        self.model = AutoModel.from_pretrained('intfloat/multilingual-e5-small')
    
    def average_pool(self, last_hidden_states: Tensor,
                    attention_mask: Tensor) -> Tensor:
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

    def embed(self, text, is_query=True):
        batch_dict = self.tokenizer(f'{"query" if is_query else "passage"}: {text}',
                            max_length=512,
                            padding=True,
                            truncation=True,
                            return_tensors='pt')

        with torch.no_grad():
            outputs = self.model(**batch_dict)
        
        embeddings = self.average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])

        # normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)

        # save embeddings
        vector = embeddings[0].numpy()
        return vector

if __name__ == '__main__':
    print('Инициализация...')
    embedder = Embedder()
    print('Инициализировано')
    print(embedder.embed(input('Введите текст: ')))