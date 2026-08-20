# Security review example

Compile:

```bash
prove-it compose \
  --task examples/security-review/task.json \
  --template audit \
  --profile security \
  --profile audit-remediation \
  --profile high-assurance-validation \
  --adapter generic \
  -o examples/security-review/compiled-prompt.md
```
