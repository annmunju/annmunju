# 20220806

* 3차 프로젝트 코드 살펴보고 해석 가능하도록 만들기
    1. __LDA__
    2. 감성사전 구축
    3. 코사인 유사도

---

## 새로운 카테고리 분류 : LDA

> 소설 카테고리를 `#` 태그 형식으로 새롭게 분류하기 위해서 LDA를 사용해 단어를 분류, 추출하고자 한다.
> 

* 사용 모듈 import

```python
import gensim
from gensim import corpora, models
from gensim.models import CoherenceModel
from gensim.test.utils import common_corpus
from gensim.models.wrappers import LdaMallet
import pyLDAvis
import pyLDAvis.gensim_models
```

1. LDA 주제 일관성(coherence) 측정 함수 작성 : **lda_coh**

```python
def lda_coh(stories, no_below=5, num_topics=4, data_word=None, data_words=None):
# pd.series 형식 데이터, 특정 횟수(5) 이상 나온 단어만, 주제 수(4), 함수를 어떻게 쓸지(아래 if문)

		# data_word를 'stop'이라고 할 때, 이야기 전체 형태소 분리하고
    if data_word == 'stop':
        data_words = []
        for story in stories:
            data = list(str(story).split())
            data_words.append(data)
            
        return data_words # 이것만 반환해주는 역할

    # 형태소 분리 후 data_words 리스트 형태로 변환해 코드에 활용
    if data_word == None:
        data_words = []
        for story in stories:
            data = list(str(story).split())
            data_words.append(data)
    
    # id2word, corpus 추출
    id2word = corpora.Dictionary(data_words)
    id2word.filter_extremes(no_below = no_below) # no_below 회 이하로 등장한 단어는 삭제
    corpus = [id2word.doc2bow(text) for text in data_words] 
				# doc2bow는 문서 단어의 id와 빈도수로 수치화 해주는 메소드
    
		# mallet : 자바 기반 자연어처리 패키지
    mallet_path = '../mallet-2.0.8/bin/mallet' 
    ldamallet = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=num_topics, random_seed=12, id2word=id2word)

    coherence_model_ldamallet = CoherenceModel(model=ldamallet, texts=texts, dictionary=id2word, coherence='c_v')
    coherence_ldamallet = coherence_model_ldamallet.get_coherence()
    
    return texts, corpus, ldamallet, coherence_ldamallet
```

2. topics 주제와