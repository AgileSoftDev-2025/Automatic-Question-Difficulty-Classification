# T5 LoRA Model for Question Regeneration

This directory contains the pre-trained T5 model with LoRA (Low-Rank Adaptation) adapters for transforming questions across Bloom's Taxonomy levels (C1-C6).

## Model Files

- `adapter_model.safetensors` - LoRA adapter weights
- `adapter_config.json` - LoRA configuration
- `tokenizer.json` - Tokenizer vocabulary and mappings
- `tokenizer_config.json` - Tokenizer configuration
- `special_tokens_map.json` - Special tokens mapping

## Model Details

- **Base Model**: T5-Small
- **Fine-tuning Method**: LoRA (Low-Rank Adaptation)
- **Purpose**: Transform/regenerate questions across Bloom's taxonomy levels
- **Training Data**: Multi-level question dataset with C1-C6 samples

## Usage

This model is used by `regenerate_utils.py` to generate variations of questions at different cognitive levels.

### Transformation Examples:
- C1 (Remember) → C3 (Apply)
- C2 (Understand) → C4 (Analyze)
- C3 (Apply) → C6 (Create)

## Performance

- Trained with efficient LoRA adapters to reduce parameter count
- Beam search decoding for high-quality generation
- Temperature-controlled sampling for diversity control
