# Cahier des charges — Plateforme de mise en relation

| | |
|---|---|
| **Version** | 0.1 — projet soumis à validation |
| **Date** | 2 juillet 2026 |
| **Statut** | À valider par la responsable produit |
| **Destinataire** | Responsable produit |
| **Objet** | Cadrer le besoin fonctionnel et les contraintes du projet, en vue des spécifications détaillées et du découpage en itérations |

> **Comment lire ce document.** Les sections 1 à 6 décrivent le *besoin* (le « quoi ») en langage métier : c'est ce que la responsable produit valide. La section 7 rassemble les *contraintes techniques* (le « comment »), qui seront détaillées ultérieurement dans les spécifications. La section 8 propose un découpage en itérations. La section 9 liste les **décisions à arbitrer** avant de passer aux spécifications : ce sont les points bloquants.

---

## 1. Contexte et objectifs

La plateforme met en relation deux populations : des **clients** exprimant un besoin et des **vendeurs / prestataires** proposant une offre. Contrairement à un site e-commerce classique, la valeur et le revenu ne proviennent **pas de la vente des produits ou services** des vendeurs, mais de la **mise en relation elle-même**.

Le moteur de mise en relation s'appuie sur les caractéristiques des deux parties, dont la **proximité géographique**, qui est un critère déterminant.

Un premier prototype visuel a été réalisé (interface statique, sans logique métier robuste). Il sert de **maquette de référence pour l'expérience utilisateur**, mais **pas de socle technique** pour la version cible.

**Objectifs du projet :**

- **OBJ-01** — Permettre à un client d'exprimer un besoin et d'obtenir une liste de vendeurs pertinents, ordonnés par adéquation.
- **OBJ-02** — Permettre à un vendeur de présenter son offre et sa zone d'intervention, et de recevoir des mises en relation qualifiées.
- **OBJ-03** — Monétiser la mise en relation selon un modèle à valider (voir §4).
- **OBJ-04** — Offrir une expérience accessible, en priorité sur mobile, adaptée à un public de seniors.
- **OBJ-05** — Proposer le service en allemand et en anglais.

---

## 2. Périmètre

### 2.1 Inclus dans le périmètre

- Gestion des comptes et profils pour les deux populations (client / vendeur).
- Saisie et gestion de l'offre vendeur, incluant la zone géographique d'intervention.
- Expression du besoin client.
- Moteur de mise en relation multicritères incluant la distance.
- Mécanisme de monétisation de la mise en relation (modèle à arbitrer, §4).
- Notifications aux parties.
- Back-office d'administration et de modération.
- Suivi d'usage (statistiques d'utilisation, base des évolutions futures du moteur).
- Interface multilingue (DE/EN), accessible, mobile-first.

### 2.2 Exclu du périmètre (au moins pour la première version)

- **HORS-01** — Traitement de la transaction commerciale finale entre client et vendeur, *si* le modèle retenu ne fait pas transiter le paiement par la plateforme (à confirmer, voir DEC-01).
- **HORS-02** — Moteur de recommandation avancé par apprentissage automatique (le moteur v1 est un scoring multicritères déterministe ; l'apprentissage est une évolution ultérieure).
- **HORS-03** — Application mobile native (le web mobile responsive couvre le besoin initial).
- **HORS-04** — Messagerie interne temps réel riche entre client et vendeur (à confirmer selon le modèle de mise en relation, DEC-02).

### 2.3 Hypothèses structurantes

- **HYP-01** — Le public cible comprend une proportion significative de seniors ; l'ergonomie et l'accessibilité sont des exigences de premier plan, non des options.
- **HYP-02** — L'usage se fera majoritairement sur téléphone mobile.
- **HYP-03** — Le contenu de l'interface est initialement en allemand ; l'anglais est requis.

---

## 3. Acteurs

| Code | Acteur | Description |
|---|---|---|
| **A-CLI** | Client | Exprime un besoin, consulte les vendeurs proposés, initie une mise en relation. |
| **A-VEN** | Vendeur / prestataire | Publie son offre et sa zone d'intervention, reçoit des mises en relation, gère son profil. |
| **A-ADM** | Administrateur / opérateur | Gère les comptes, modère les contenus, supervise la facturation et les statistiques. |
| **A-SYS** | Systèmes externes | Fournisseur d'authentification, service de paiement, service d'envoi d'e-mails, service de géocodage. |

---

## 4. Modèle économique

Le revenu provient de la mise en relation. Le mécanisme précis reste à arbitrer (voir DEC-03) parmi les options suivantes, non exclusives :

- **Paiement à la mise en relation (pay-per-lead)** — le vendeur paie pour chaque demande qualifiée qui lui est transmise.
- **Déblocage de contact** — la coordonnée du vendeur (ou du client) est masquée jusqu'à un paiement / une action.
- **Abonnement vendeur** — accès à la plateforme et/ou visibilité accrue contre un abonnement périodique.
- **Commission au succès** — perçue lorsqu'une mise en relation aboutit (nécessite un mécanisme de suivi de l'aboutissement).

Le choix de modèle **conditionne fortement** les exigences fonctionnelles de la section 5.6 et l'architecture (voir DEC-01, DEC-03).

---

## 5. Exigences fonctionnelles

> Convention : `EF-xx` = exigence fonctionnelle. Priorité : **M** (must / indispensable v1), **S** (should / souhaitable), **C** (could / ultérieur).

### 5.1 Comptes et profils

| Code | Exigence | Prio |
|---|---|---|
| EF-01 | Un visiteur peut créer un compte client ou un compte vendeur. | M |
| EF-02 | Authentification par e-mail + mot de passe, avec vérification d'e-mail et réinitialisation de mot de passe. | M |
| EF-03 | Un utilisateur peut consulter et modifier son profil, et supprimer son compte (droit à l'effacement, voir §6.6). | M |
| EF-04 | Chaque profil porte une **langue préférée** (DE/EN), utilisée pour l'interface, les e-mails et les notifications. | M |
| EF-05 | Connexion via fournisseur tiers (Google, etc.). | S |

### 5.2 Profil et offre vendeur

| Code | Exigence | Prio |
|---|---|---|
| EF-10 | Un vendeur décrit son offre : catégorie(s), description, éléments de présentation (texte, images). | M |
| EF-11 | Un vendeur définit sa **zone d'intervention géographique** (voir §5.5 pour les modalités). | M |
| EF-12 | Un vendeur peut indiquer sa disponibilité (actif / en pause). | M |
| EF-13 | Le contenu descriptif du profil peut être fourni dans les langues supportées (voir DEC-04 sur le multilinguisme des données). | S |
| EF-14 | Un vendeur consulte l'historique des mises en relation le concernant. | M |

### 5.3 Expression du besoin client

| Code | Exigence | Prio |
|---|---|---|
| EF-20 | Un client exprime son besoin via un parcours guidé simple (catégorie, précisions, localisation). | M |
| EF-21 | Le parcours est **minimal en nombre d'étapes** et explicite (contrainte senior, voir §6.1). | M |
| EF-22 | Le client fournit sa localisation (voir §5.5). | M |
| EF-23 | Un client retrouve l'historique de ses demandes et des mises en relation associées. | S |

### 5.4 Moteur de mise en relation

Le moteur v1 est un **scoring multicritères déterministe** : à une demande client, il associe un score d'adéquation à chaque vendeur candidat, puis retourne les mieux classés. Il reste volontairement simple et explicable.

| Code | Exigence | Prio |
|---|---|---|
| EF-30 | Pour une demande client, le moteur établit la liste des vendeurs candidats et les ordonne par score d'adéquation décroissant. | M |
| EF-31 | Le score combine plusieurs critères pondérés, dont au minimum : adéquation de la catégorie / du besoin, **proximité géographique** (§5.5), disponibilité du vendeur. | M |
| EF-32 | Les pondérations des critères sont **configurables** par l'administrateur, sans redéploiement. | S |
| EF-33 | Le moteur exclut les vendeurs hors zone / indisponibles / ne couvrant pas la catégorie demandée. | M |
| EF-34 | Le résultat affiché au client indique la **distance** au vendeur et les éléments justifiant la pertinence. | M |
| EF-35 | Le moteur consigne, pour chaque mise en relation, les critères et le score retenus (traçabilité, base d'amélioration future). | S |
| EF-36 | Évolution ultérieure : ajustement du classement à partir des préférences et de l'usage observé (apprentissage). | C |

### 5.5 Géolocalisation et distance

La distance entre client et vendeur est un critère central du moteur. Ce domaine mérite un traitement explicite.

| Code | Exigence | Prio |
|---|---|---|
| EF-40 | Le vendeur définit sa zone d'intervention. **Modalité à arbitrer** (DEC-05) : rayon autour d'un point d'ancrage, ou liste de zones administratives (cantons / communes / codes postaux), ou combinaison. | M |
| EF-41 | La localisation du client est obtenue par saisie d'adresse / code postal, et/ou géolocalisation de l'appareil (avec consentement). | M |
| EF-42 | Le système calcule la distance client ↔ vendeur et l'utilise comme critère de score (EF-31) et comme information affichée (EF-34). | M |
| EF-43 | La précision de localisation stockée doit être **minimale et proportionnée** : un niveau de précision réduit (code postal / localité) est privilégié si le besoin métier le permet (voir §6.6). | M |
| EF-44 | L'utilisateur est informé de l'usage de sa localisation et y consent explicitement. | M |
| EF-45 | Gestion des cas limites : localisation absente ou imprécise (le moteur doit rester fonctionnel avec un critère distance dégradé plutôt que d'échouer). | S |

### 5.6 Monétisation de la mise en relation

*(Ces exigences dépendent du modèle retenu en §4 / DEC-03 ; à préciser une fois l'arbitrage rendu.)*

| Code | Exigence | Prio |
|---|---|---|
| EF-50 | Le système enregistre chaque mise en relation comme un événement facturable (ou consommateur de crédit / quota), selon le modèle retenu. | M |
| EF-51 | Encaissement via un prestataire de paiement externe ; **aucune donnée sensible de paiement ne transite ni n'est stockée par la plateforme**. | M |
| EF-52 | La confirmation de paiement provient exclusivement du prestataire (mécanisme serveur vérifié), jamais d'une action côté navigateur. | M |
| EF-53 | Le vendeur (et/ou l'administrateur) consulte l'historique de facturation / consommation. | M |
| EF-54 | Gestion des quotas / crédits / limites selon le modèle (ex. plafond de mises en relation par période). | S |

### 5.7 Recherche et découverte

| Code | Exigence | Prio |
|---|---|---|
| EF-60 | Un client peut parcourir / rechercher les vendeurs par catégorie et zone, en dehors du parcours de mise en relation. | S |
| EF-61 | Filtres simples (catégorie, distance, disponibilité). | S |

### 5.8 Notifications et communication

| Code | Exigence | Prio |
|---|---|---|
| EF-70 | Le vendeur est notifié d'une nouvelle mise en relation le concernant (e-mail au minimum ; notification en temps réel dans l'interface souhaitée). | M |
| EF-71 | Le client est notifié du résultat / de la prise en compte de sa demande. | M |
| EF-72 | Les notifications respectent la langue préférée du destinataire (EF-04). | M |
| EF-73 | Modalités d'échange ultérieur entre les parties après mise en relation : **à arbitrer** (DEC-02) — coordonnées échangées vs messagerie interne. | S |

### 5.9 Back-office / administration

| Code | Exigence | Prio |
|---|---|---|
| EF-80 | L'administrateur gère les comptes (validation, suspension, suppression). | M |
| EF-81 | L'administrateur modère les contenus (profils, descriptions). | M |
| EF-82 | L'administrateur configure les catégories et les pondérations du moteur (EF-32). | S |
| EF-83 | L'administrateur consulte les statistiques d'usage et de facturation. | M |

### 5.10 Suivi d'usage (analytique)

| Code | Exigence | Prio |
|---|---|---|
| EF-90 | Le système consigne les événements d'usage clés (demandes, mises en relation, consultations, déblocages). | M |
| EF-91 | Ces données alimentent les statistiques d'administration et, à terme, l'amélioration du moteur (EF-36). | S |
| EF-92 | La collecte respecte les principes de minimisation et de consentement (§6.6). | M |

---

## 6. Exigences non-fonctionnelles

> Convention : `ENF-xx`.

### 6.1 Accessibilité et adaptation au public senior

C'est une exigence **structurante**, à concevoir dès l'origine de l'interface, non à ajouter après coup.

| Code | Exigence |
|---|---|
| ENF-01 | Conformité visée au référentiel **WCAG 2.2 niveau AA** : contrastes suffisants, tailles de texte confortables et redimensionnables sans rupture de mise en page, cibles tactiles ≥ 44 px, focus visible, navigation clavier complète, compatibilité lecteurs d'écran, HTML sémantique et attributs ARIA. |
| ENF-02 | Adaptation senior au-delà de WCAG : parcours courts et linéaires, libellés explicites plutôt qu'icônes seules, messages d'erreur clairs et tolérants, absence d'interactions dépendant du survol, cohérence forte des écrans. |
| ENF-03 | Tests d'accessibilité et tests d'utilisabilité auprès d'utilisateurs représentatifs (dont seniors) prévus dans le processus. |

### 6.2 Multilinguisme

| Code | Exigence |
|---|---|
| ENF-10 | L'interface est disponible en allemand et en anglais, avec sélecteur de langue et respect de la langue préférée du profil (EF-04). |
| ENF-11 | L'architecture d'internationalisation permet d'ajouter d'autres langues sans refonte. |
| ENF-12 | Le multilinguisme des **contenus dynamiques** (descriptions vendeurs, catégories) est traité selon l'arbitrage DEC-04. |

### 6.3 Mobile-first et responsive

| Code | Exigence |
|---|---|
| ENF-20 | Conception **mobile-first** : l'expérience est optimisée pour le téléphone en priorité, puis adaptée aux écrans plus grands. |
| ENF-21 | Fonctionnement sur les navigateurs mobiles récents (iOS Safari, Android Chrome) et sur desktop. |

### 6.4 Performance

| Code | Exigence |
|---|---|
| ENF-30 | Temps de réponse du moteur de mise en relation perçu comme immédiat (objectif indicatif < 2 s pour une demande, à préciser en specs). |
| ENF-31 | Interface fluide sur connexion mobile de qualité moyenne. |

### 6.5 Sécurité

| Code | Exigence |
|---|---|
| ENF-40 | Toute opération sensible (facturation, déblocage, écriture des données critiques) est exécutée et validée **côté serveur** ; le navigateur ne fait jamais autorité. |
| ENF-41 | Autorisation centralisée en un seul point de vérité (voir §7), pour éviter la divergence des règles d'accès. |
| ENF-42 | Chiffrement des échanges (HTTPS), gestion sûre des secrets, journalisation des accès sensibles. |

### 6.6 Protection des données personnelles

Le traitement de données personnelles, **et en particulier de localisation**, impose une conformité réglementaire à préciser selon les publics visés.

| Code | Exigence |
|---|---|
| ENF-50 | Conformité à la loi suisse sur la protection des données (**nLPD / révision de la LPD**) et, si des personnes situées dans l'UE sont concernées, au **RGPD**. Le périmètre réglementaire exact est à confirmer (DEC-06). |
| ENF-51 | **Minimisation** : ne collecter que les données nécessaires ; pour la localisation, privilégier la granularité la plus faible suffisante au métier (EF-43). |
| ENF-52 | Consentement explicite pour la géolocalisation et la collecte d'usage ; information claire sur les finalités. |
| ENF-53 | Exercice des droits : accès, rectification, effacement (cohérent avec EF-03), portabilité le cas échéant. |
| ENF-54 | Politique de conservation définie (durée de vie des demandes, des localisations, des événements d'usage). |

### 6.7 Maintenabilité et transmissibilité

| Code | Exigence |
|---|---|
| ENF-60 | La technologie principale doit rester **maintenable par une entreprise non technique** via un prestataire : le choix se porte sur **Python** (bassin de compétences large, courbe d'apprentissage douce). |
| ENF-61 | Le code, le schéma de données et le contrat d'interface sont documentés de façon à permettre une reprise par un tiers. |
| ENF-62 | Éviter toute complexité technologique non justifiée par le besoin (principe de sobriété d'architecture). |

---

## 7. Contraintes techniques

> *Annexe destinée à cadrer les spécifications ; ne requiert pas de validation métier détaillée de la part de la responsable produit. Ces choix seront détaillés et pourront évoluer en phase de spécifications.*

- **Backend : Python.** Pour la maintenabilité et la transmissibilité (ENF-60). Le domaine métier (profils, moteur de mise en relation, monétisation) et l'interface applicative (API) sont implémentés en Python.
- **Base de données et services de base : Supabase**, utilisé comme **PostgreSQL managé** entouré de ses services d'authentification, de stockage de fichiers et de notifications temps réel. La logique métier ne réside **pas** dans la base : celle-ci porte l'intégrité des données (contraintes, transactions), le backend Python porte la logique.
- **Point d'autorité unique pour l'autorisation** : l'accès aux données passe par le backend, qui est le seul lieu où s'appliquent les règles métier d'accès (ENF-41). Les mécanismes de sécurité au niveau base sont, le cas échéant, une défense en profondeur, pas la source de vérité.
- **Géodonnées** : la gestion des distances et des zones s'appuie sur les capacités géospatiales de PostgreSQL (extension géospatiale disponible dans Supabase), à confirmer selon la modalité de zone retenue (DEC-05). Un service de géocodage externe convertit les adresses en coordonnées.
- **Interface (front)** : le prototype existant sert de **référence UX**, pas de base de code. L'interface cible est reconstruite pour satisfaire accessibilité, multilinguisme et mobile-first, et communique avec le backend via son API (jamais directement avec la base).
- **Stratégie prototype → cible** : un prototype rapide est acceptable pour valider le parcours et le moteur, à condition de préserver dès le départ les éléments durables — **schéma de données** et **contrat d'API** — qui doivent survivre à une refonte de l'implémentation. Le moteur de mise en relation pourra, si nécessaire et si les compétences de maintenance le permettent, être isolé dans un service dédié plus performant ultérieurement, sans changer le schéma.

---

## 8. Proposition de découpage en itérations

*(Indicatif, à affiner avec la responsable produit après validation du périmètre.)*

**Itération 0 — Cadrage et socle durable**
Validation du présent cahier des charges, arbitrage des décisions §9, définition du schéma de données et du contrat d'API, choix de la modalité de zone géographique et du modèle de monétisation.

**Itération 1 — MVP fonctionnel**
Comptes et profils (EF-01→04, EF-10→12), expression du besoin (EF-20→22), géolocalisation de base (EF-40→44), moteur de mise en relation v1 (EF-30→34), notification e-mail (EF-70→72), back-office minimal (EF-80, EF-83). Interface accessible, mobile-first, DE/EN sur les écrans du parcours principal.

**Itération 2 — Monétisation**
Mécanisme de facturation de la mise en relation selon le modèle retenu (EF-50→54), historique de facturation, back-office de supervision.

**Itération 3 — Enrichissement**
Recherche / découverte (EF-60→61), configuration des pondérations (EF-32), multilinguisme des contenus dynamiques (EF-13), notifications temps réel (EF-70), suivi d'usage complet (EF-90→92).

**Itérations ultérieures**
Amélioration du moteur par apprentissage de l'usage (EF-36), éventuelle application native, langues supplémentaires.

---

## 9. Décisions à arbitrer par la responsable produit

Ces points conditionnent les spécifications et doivent être tranchés avant l'itération 1.

| Code | Décision | Impact |
|---|---|---|
| **DEC-01** | Le paiement du service final entre client et vendeur **transite-t-il par la plateforme**, ou la plateforme ne facture-t-elle **que la mise en relation** ? | Détermine l'ampleur des besoins transactionnels et une part de l'architecture. |
| **DEC-02** | Après mise en relation, les parties échangent-elles via des **coordonnées communiquées** ou via une **messagerie interne** ? | Impacte EF-73, la vie privée et le périmètre v1. |
| **DEC-03** | Quel **modèle de monétisation** (§4) : pay-per-lead, déblocage de contact, abonnement, commission au succès, ou combinaison ? | Conditionne toute la section 5.6. |
| **DEC-04** | Les **contenus dynamiques** (descriptions vendeurs, catégories) sont-ils **multilingues** (DE + EN) ou en allemand seul ? | Décision de **schéma de données** à prendre tôt (coûteuse à rattraper). |
| **DEC-05** | Comment un vendeur définit-il sa **zone d'intervention** : rayon autour d'un point, zones administratives (cantons/communes/codes postaux), ou combinaison ? | Détermine le modèle géospatial et l'ergonomie de saisie. |
| **DEC-06** | Quel **périmètre réglementaire** : uniquement Suisse (nLPD), ou aussi utilisateurs UE (RGPD) ? | Impacte les exigences de conformité (§6.6). |
| **DEC-07** | Quels sont les **critères et pondérations initiaux** du moteur de mise en relation, au-delà de catégorie / distance / disponibilité ? | Précise EF-31. |

---

*Fin du document — version 0.1 soumise à validation.*
