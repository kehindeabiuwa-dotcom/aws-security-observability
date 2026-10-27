# Testing and verification

## Local checks

Checked on 27 October 2026:

- CloudFormation validation with `cfn-lint 1.46.0`.
- Five regression tests for infrastructure boundaries and remote-command result handling.
- Python syntax and command-line help.
- Relative document links, image paths and Dev.to front matter.
- Screenshot checksums against the source manifest.

## Repeat the checks

```bash
python3 -m pip install -r requirements-dev.txt
cfn-lint infrastructure/*.json
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
```

## AWS checks

Follow the [deployment guide](deployment.md) to run the project checks in your account. Record command outputs, relevant logs and screenshots using the [evidence checklist](../evidence/README.md).

## Publication checks

See [publishing instructions](publishing.md) for the repository name, branch, hosted-image paths and Dev.to steps.
