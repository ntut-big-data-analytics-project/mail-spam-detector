# coding: utf-8
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer

from email_helper import *

eml_path = "Y:\\2c23eff186c76668c7bec9db096a65eb.eml"  # if len(sys.argv) != 3 else sys.argv[2]
write_path = "zxcv"
model_path = "m.h5"

# print(HanziConv.toTraditional(str))
seg_list = process_email(eml_path)

with open(write_path, "w+", encoding='utf8') as f:
    f.write(EMAIL_CONTENT_DELIMITER.join(seg_list))

model = load_model(model_path)

s = []
k = ''
with open(write_path, 'r', encoding='utf8') as f:
    k = f.read().replace("\n", "/").replace(" ", "").split("/")
while True:
    k_index = k.index('') if '' in k else -1
    if k_index == -1:
        break
    k.pop(k_index)
print(k)
s += [k]

templ = len(s)
tokenizer = Tokenizer()
tokenizer.fit_on_texts(list(s))
sequences = tokenizer.texts_to_sequences(s)
data = pad_sequences(sequences, maxlen=200)
print(sequences)
print(data)

y = model.predict_classes(data)

print('spam' if (y[0] == 0) else 'ham')
# category={'spam': 0, 'ham': 1}
