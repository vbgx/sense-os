# Sense-OS

Sense-OS est une plateforme d'intelligence collective en temps réel 
qui détecte, analyse et classe les "pains" (problèmes, tendances, questions) 
exprimés par des communautés en ligne (par exemple, Reddit, Hacker News). 
Grâce à un pipeline de traitement distribué, 
Sense-OS transforme des signaux bruts en insights exploitables 
tout en mettant l'accent sur l'idempotence, la performance et la scalabilité.

## 📌 Table des Matières

Architecture
Composants
Prérequis
Installation
Utilisation
Validation
Développement
Tests
Contribuer
Licence

---

## 🏗️ Architecture

Sense-OS adopte une architecture modulaire et distribuée, 
divisée en plusieurs workers spécialisés et une API REST pour la gestion des interactions. 

Les principaux composants sont :

- Ingestion Worker : Récupère les signaux depuis des sources externes (Reddit, Hacker News, etc.).

- Processing Worker : Extrait les caractéristiques des signaux, calcule les scores de "pain", et stocke les instances.

- Clustering Worker : Regroupe les signaux similaires en clusters thématiques.

- Trend Worker : Calcule les métriques de tendance (vélocité, émergence, déclin).

- API Gateway : Fournit une interface REST pour interagir avec les données (pains, tendances, clusters).

- Scheduler : Orchestration et planification des jobs de traitement.

- Base de données PostgreSQL : Stocke les signaux, clusters et métriques.

- Redis : Gère la communication asynchrone entre les workers.

---

## 🧩 Composants

| Composant             | Description                                                                     | Dossier                           |
| --------------------- | ------------------------------------------------------------------------------- | --------------------------------- |
| **Ingestion Worker**  | Récupère et normalise les signaux depuis des sources externes.                  | `services/ingestion_worker`       |
| **Processing Worker** | Traite les signaux pour extraire des "pains" (problèmes, questions, tendances). | `services/processing_worker`      |
| **Clustering Worker** | Regroupe les signaux en clusters thématiques.                                   | `services/clustering_worker`      |
| **Trend Worker**      | Calcule les métriques de tendance (vélocité, émergence, déclin).                | `services/trend_worker`           |
| **API Gateway**       | Fournit une API REST pour accéder aux données.                                  | `apps/api_gateway`                |
| **Scheduler**         | Planifie et orchestre les jobs pour les workers.                                | `services/scheduler`              |
| **Base de données**   | Stocke les signaux, clusters, et métriques (migrations Alembic).                | `packages/db/src/db/migrations`  |
| **Files Redis**       | Gère la communication asynchrone entre les workers.                             | `infra/docker/docker-compose.yml` |

---

## 📋 Prérequis

Avant de commencer, vous devez avoir les éléments suivants installés :

- Docker et Docker Compose pour exécuter les services en local.

- Python 3.12 pour le développement local.

- PostgreSQL et Redis (gérés via docker-compose.yml).

- Make pour utiliser les commandes du Makefile.

---

## 🚀 Installation

1- Cloner le dépôt :

```bash
git clone https://github.com/votre-org/sense-os.git
cd sense-os`
```

2- Configurer l'environnement :

```bash
cp .env.example .env
```
Modifiez le fichier .env selon vos besoins (par exemple, les variables de base de données, clés API, etc.).

3- Démarrer les services :

```bash
make up
```
Cette commande démarre tous les services (PostgreSQL, Redis, API Gateway et workers).

4- Appliquer les migrations :

```bash
make migrate
```


5- Seed de la base de données :

```bash
make seed
```

---

## 🎯 Utilisation

- Lancer un job manuel : Pour lancer un job d'ingestion et de traitement pour un vertical spécifique (ex. : saas depuis Reddit) :

```bash
make scheduler-once VERTICAL_ID=1 SOURCE=reddit QUERY=saas LIMIT=50
```

- Calculer les tendances : Pour calculer les tendances d'un jour spécifique :

```bash
make trend-once VERTICAL_ID=1 DAY=2026-02-15
```

- Accéder à l'API : L'API est disponible à l'adresse http://localhost:8000
. Les endpoints disponibles :

GET /pains : Liste des "pains" détectés.

GET /pains/{id} : Détails d'un "pain".

GET /trending : Clusters en tendance.

GET /emerging : Clusters émergents.

GET /declining : Clusters en déclin.

---

## ✅ Validation

Pour vérifier que tout fonctionne correctement, utilisez la commande suivante :

```bash
make validate
```
Cette commande arrête les services existants, applique les migrations, seed la base de données, et lance un job d'ingestion et de traitement pour vérifier que les données sont accessibles via l'API.

---

## 🛠️ Développement

Structure du projet

.sense-os/
├── apps/               # Applications (API Gateway)
├── services/           # Workers (ingestion, processing, clustering, trend, scheduler)
├── packages/           # Bibliothèques partagées (db, domain, queue)
├── infra/              # Infrastructure (Docker, SQL)
├── docs/               # Documentation
├── tools/              # Scripts utilitaires
└── Makefile            # Commandes utiles

Ajouter une nouvelle source de données

Créez un adapter dans `services/ingestion_worker/src/ingestion_worker/adapters/`.

Configurez le vertical dans `tools/fixtures/verticals/`.

Mettez à jour le scheduler pour inclure la nouvelle source.

Développer localement

Pour exécuter un worker localement sans Docker, utilisez :

```bash
make workers-local
```


Puis, dans un terminal séparé, lancez :

```bash
./tools/scripts/run_processing_worker.sh
```

---

## 🧪 Tests

Tests unitaires : Les tests se trouvent dans les dossiers tests/ de chaque service. Pour les exécuter :

```bash
cd services/processing_worker
pytest
```


Test d'idempotence : Pour tester l'idempotence du Processing Worker :

```bash
make test-processing-idempotence
```

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Voici comment contribuer :

Fork le projet.

Créez une branche pour votre fonctionnalité (par exemple, git checkout -b feature/ma-fonctionnalité).

Committez vos changements (ex. git commit -am 'Ajout de ma fonctionnalité').

Poussez la branche (git push origin feature/ma-fonctionnalité).

Ouvrez une Pull Request.

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

Points clés

Clarté : Explication simple et claire de l'architecture et des composants.

Pratique : Commandes simples et directes avec make pour l'installation, la validation et les tests.

Modularité : Structure du projet bien définie et guide pour ajouter de nouvelles sources.

Idempotence : Mise en avant du test d'idempotence pour garantir la stabilité des processus.

API : Documentation complète des endpoints disponibles pour interagir avec les données.
