# Stage 4b — Sign & attest (supply-chain provenance)

> **AI Attribution:** AI-assisted (Claude, Anthropic); reviewed and validated by Mohammad Sinan Ali.

| Attribute | Specification |
|---|---|
| Tool & version | Cosign 2.x keyless (GitHub OIDC → Fulcio, Rekor transparency log) · in-toto / SLSA provenance |
| Execution | after stage 4; ∥ with 3, 5 |
| SLA (est. duration) | **2 min** |
| Inputs | Image digest from stage 4. |
| Outputs | Signature + SBOM attestation + SLSA provenance stored next to the image. |
| Regulatory mapping | RBI 6.1, 7.2; PCI 6.3 |

## Configuration & thresholds (blocking)
- Sign by **digest**, never by tag
- Attach CycloneDX SBOM and provenance attestations
- Identity pinned to `https://github.com/novapay/*` workflows

## Failure mode
Signature/attestation missing or identity mismatch → image cannot be admitted (Kyverno `verifyImages`).

## Remediation guidance
Re-run signing job; investigate if identity mismatch (possible tampering).

## Retry / skip / exception logic
Retry: 1×. Skip: **never**.

## Reference configuration
```bash
cosign sign --yes $IMAGE@$DIGEST
cosign attest --yes --type cyclonedx --predicate sbom.cdx.json $IMAGE@$DIGEST
```

[← Architecture](../architecture.md) · every result is written to the audit store (schema in [D3](../../03-compliance-gates/compliance-gates.md#5-structured-audit-record-json-schema)).
