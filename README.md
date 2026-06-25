# Detection as Code

Pipeline CI/CD de détection des menaces basé sur [Sigma](https://github.com/SigmaHQ/sigma). Les règles de détection sont versionnées dans Git, validées et testées automatiquement via GitHub Actions contre un vrai Elasticsearch avant chaque merge.

## Architecture

```
Pull Request
    │
    ▼
validate.yml
    ├── Lint (sigma check)       — vérifie la syntaxe et le tagging MITRE ATT&CK
    └── Tests (Elasticsearch)    — vérifie les true/false positifs contre un container ES

Merge dans main
    │
    ▼
deploy.yml
    └── Conversion Lucene        — génère les requêtes prêtes à déployer (artefacts)
```

## Règles disponibles

| Règle | Technique MITRE | Sévérité |
|---|---|---|
| SSH Brute Force Attempt | T1110.001 | Medium |
| Sudo Abuse — Shell Escalation | T1548.003 | High |

## Structure du projet

```
detection-as-code/
├── detections/
│   └── linux/
│       ├── ssh_brute_force.yml
│       └── sudo_abuse.yml
├── tests/
│   └── linux/
│       ├── ssh_brute_force/
│       │   ├── true_positive.json
│       │   └── false_positive.json
│       └── sudo_abuse/
│           ├── true_positive.json
│           └── false_positive.json
├── .github/workflows/
│   ├── validate.yml
│   └── deploy.yml
└── tests/
    └── test_with_es.py
```

## Comment contribuer une règle

1. Créez une branche : `git checkout -b feature/nom-de-la-regle`
2. Ajoutez la règle dans `detections/<os>/<nom>.yml` au format Sigma
3. Ajoutez les données de test dans `tests/<os>/<nom>/true_positive.json` et `false_positive.json`
4. Ouvrez une Pull Request — le pipeline valide et teste automatiquement
5. Après review et merge, `deploy.yml` génère les règles converties

## Format des règles

Les règles suivent le standard [Sigma](https://sigmahq.io/). Exemple minimal :

```yaml
title: Nom de la règle
id: <uuid>
status: experimental
description: Ce que détecte la règle et pourquoi c'est suspect
references:
    - https://attack.mitre.org/techniques/TXXXX/
author: Quentin Estienne
date: YYYY/MM/DD
tags:
    - attack.tXXXX.XXX
logsource:
    product: linux
    service: auth
detection:
    selection:
        Message|contains: 'pattern'
    condition: selection
level: low/medium/high/critical
falsepositives:
    - Cas légitimes connus
```

## Stack technique

- **Sigma** : format ouvert pour les règles de détection, convertible vers Splunk, Elasticsearch, QRadar, etc.
- **sigma-cli** : validation et conversion des règles
- **Elasticsearch 8.11** : SIEM cible pour les tests d'intégration
- **GitHub Actions** : orchestration du pipeline CI/CD
