# This file was auto-generated by Fern from our API Definition.

import typing
from .open_ai_vectorizer_text_embedding_3_small_request import OpenAiVectorizerTextEmbedding3SmallRequest
from .open_ai_vectorizer_text_embedding_3_large_request import OpenAiVectorizerTextEmbedding3LargeRequest
from .open_ai_vectorizer_text_embedding_ada_002_request import OpenAiVectorizerTextEmbeddingAda002Request
from .basic_vectorizer_intfloat_multilingual_e_5_large_request import BasicVectorizerIntfloatMultilingualE5LargeRequest
from .basic_vectorizer_sentence_transformers_multi_qa_mpnet_base_cos_v_1_request import (
    BasicVectorizerSentenceTransformersMultiQaMpnetBaseCosV1Request,
)
from .basic_vectorizer_sentence_transformers_multi_qa_mpnet_base_dot_v_1_request import (
    BasicVectorizerSentenceTransformersMultiQaMpnetBaseDotV1Request,
)
from .hkunlp_instructor_xl_vectorizer_request import HkunlpInstructorXlVectorizerRequest
from .google_vertex_ai_vectorizer_text_embedding_004_request import GoogleVertexAiVectorizerTextEmbedding004Request
from .google_vertex_ai_vectorizer_text_multilingual_embedding_002_request import (
    GoogleVertexAiVectorizerTextMultilingualEmbedding002Request,
)

IndexingConfigVectorizerRequest = typing.Union[
    OpenAiVectorizerTextEmbedding3SmallRequest,
    OpenAiVectorizerTextEmbedding3LargeRequest,
    OpenAiVectorizerTextEmbeddingAda002Request,
    BasicVectorizerIntfloatMultilingualE5LargeRequest,
    BasicVectorizerSentenceTransformersMultiQaMpnetBaseCosV1Request,
    BasicVectorizerSentenceTransformersMultiQaMpnetBaseDotV1Request,
    HkunlpInstructorXlVectorizerRequest,
    GoogleVertexAiVectorizerTextEmbedding004Request,
    GoogleVertexAiVectorizerTextMultilingualEmbedding002Request,
]
