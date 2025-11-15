# RoBERTa Model for Bloom's Taxonomy Classification

## Required Files

Place these files in this directory:

- `config.json` - Model configuration
- `model.safetensors` - Model weights (~500MB)
- `tokenizer.json` - Tokenizer
- `tokenizer_config.json` - Tokenizer config
- `special_tokens_map.json` - Special tokens
- `vocab.json` - Vocabulary
- `merges.txt` - BPE merges

## Download

The model files are not included in the repository due to their large size.

Contact the project administrator or download from [model source].

## Setup

1. Place all model files in this directory
2. Run test: `python manage.py test_model`
3. Expected output: Model loads successfully with "C2 (Understand)" prediction