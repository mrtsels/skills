# HuggingFace Model Compatibility Patching

When loading a HuggingFace model (`AutoModel.from_pretrained` / `trust_remote_code`) with a newer transformers version than the model's vendored code expects, the custom `configuration_*.py` and `processing_*.py` files in the HuggingFace cache will fail on API changes.

## Diagnosis

Run the failing import once and read the full traceback:

```
AttributeError: 'Florence2LanguageConfig' object has no attribute 'forced_bos_token_id'
AttributeError: RobertaTokenizer has no attribute 'additional_special_tokens'
AttributeError: 'Florence2ForConditionalGeneration' object has no attribute '_supports_sdpa'
ImportError: requires einops
```

The traceback reveals which file in `~/.cache/huggingface/modules/transformers_modules/` caused the error.

## Fix Priorities

1. **Patch the cached file** (fastest — one-liner `hasattr` / `getattr` guard)
2. **Pin transformers** to a version the model supports (`pip install "transformers<4.48"`)
3. **Install missing deps** (einops, etc.)

## Common Fixes

| Error | Fix |
|-------|-----|
| `forced_bos_token_id` missing | Add `if not hasattr(self, "forced_bos_token_id"): self.forced_bos_token_id = None` before the check in `configuration_florence2.py` |
| `additional_special_tokens` missing | Replace `tokenizer.additional_special_tokens` with `getattr(tokenizer, 'additional_special_tokens', [])` in `processing_florence2.py` |
| `_supports_sdpa` missing | Cannot patch — pin transformers to `<4.48` |
| `einops` not found | `pip install einops` |

## Patched Files Location

```
~/.cache/huggingface/modules/transformers_modules/<org>/<model>/<hash>/
  ├── configuration_<model>.py
  ├── processing_<model>.py
  └── modeling_<model>.py
```

Both the base model and `-ft` (fine-tuned) variants have separate cache entries; patch both.

## Rule

Do NOT substitute the user's chosen model when compatibility fails. Fix the issue. Patching cached config/processing files is a 30-second edit and preserves the user's original intent.
