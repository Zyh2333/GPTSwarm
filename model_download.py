from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
model.save('./my_local_model/')  # 保存到本地目录
