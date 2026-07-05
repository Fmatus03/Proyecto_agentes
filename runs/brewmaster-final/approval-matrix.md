# Approval matrix

| action | default | approval required |
|---|---|---|
| external_write | denied | yes |
| deploy | denied | yes + rollback |
| production_data | denied | yes + data policy |
| persistent_memory_activation | denied | yes + evals + rollback |
| new_dependency | denied | yes + license + CVE scan |
