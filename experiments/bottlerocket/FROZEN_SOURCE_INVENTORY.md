# Frozen Bottlerocket production-root source inventory

Freeze point: after HTTP/source discovery, before any native TUF chain verification.

Source family: Bottlerocket public updater metadata.
Variant: aws-k8s-1.35
Architecture: x86_64
Metadata base: https://updates.bottlerocket.aws/2020-07-07/aws-k8s-1.35/x86_64/

Discovery result:
- unnumbered root.json: HTTP 403 (not admitted)
- 1.root.json through 8.root.json: HTTP 200 and parsed signed.version == filename version
- 9.root.json through 20.root.json: HTTP 403
- Primary root chain is therefore exactly versions 1..8, with no outcome-based filtering.

| version | sha256 | bytes |
|---:|---|---:|
| 1 | 00de549aa4530ded00512447508eb12bd578a648274c5d1275da8be2be30e7ad | 10974 |
| 2 | 29ea7bdae4dba933f265a3ad0cc455e9c5ce2f8bd4c92d2faf11c1216a12d8bb | 13632 |
| 3 | bc40b6d0c4ff2f5ab6e383d038ad9a4a6f91fb8aaebb4ee181dd587520073570 | 13632 |
| 4 | 337ee02a126edff54d690794f7171f5942b333e575a1859e634190e53608f568 | 13632 |
| 5 | 069468b7465d469ca1176f2916261c241151bc36247bf858038094d2822917b2 | 13632 |
| 6 | 80fbab56524c751eedeeb64592eccea85a4e817481c7408e96d0edc053c3344c | 13632 |
| 7 | 22e447b5b49430f98844a0c4b7532904ec98f0261bdcff7e4f4f1cd2d95e0e78 | 13632 |
| 8 | c8a0b25a1ecaa5f9531f4cc02bab1d771454d8027998d0c833c35966feb167ba | 13632 |

Scientific boundary:
- HTTP 403 for version 9 is an observed source boundary, not evidence of a failed TUF transition.
- We do not synthesize version 9, substitute another variant after seeing results, or treat inaccessible files as zero-effect negatives.
- Native verification will start from production-authored version 1 as the registered initial trust anchor and feed versions 2..8 in exact order.
