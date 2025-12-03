#! /usr/bin/env python3
# -*- coding:utf8 -*-

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
import random

api = FastAPI(
    title="API Quiz FLE - Grammaire Française",
    description="""API pour un quiz de grammaire française destiné aux apprenants de FLE (Français Langue Étrangère).

**Source pédagogique :** Questions basées sur la série *Grammaire Progressive du Français* (Éditions CLE International), ouvrage de référence dans l'enseignement du FLE.

**Volumes de la série :**
- Débutant (A1–A2)
- Intermédiaire (B1–B2)
- Avancé (B2–C1)
- Perfectionnement (C1–C2)

**Fonctionnalités :**
- Générer des quiz par niveau (A, B, C)
- Consulter les statistiques de la base des données
- Ajouter de nouvelles questions
""",
    version="1.0.0",
    contact={
        "name": "Projet ALAO - M2 IDL"
    },
    license_info={
        "name": "MIT"
    }
)

# CORS configuration - allows frontend applications to access the API
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@api.get('/')
def get_index():
    """Retourne les informations générales sur l'API et la liste des endpoints disponibles."""
    return {
        "nom": "API Quiz FLE - Grammaire Française",
        "version": "1.0.0",
        "endpoints": {
            "/": "Informations sur l'API",
            "/verify": "Vérifier le fonctionnement",
            "/generate_quiz": "Générer un quiz",
            "/create_question": "Ajouter une question",
            "/stats": "Statistiques de la base",
            "/docs": "Documentation interactive"
        }
    }

@api.get("/verify")
def verify():
    """Vérifie que l'API fonctionne correctement et retourne le nombre de questions dans la base."""
    return {
        "status": "OK",
        "message": "L'API fonctionne correctement",
        "nombre_questions": len(data)
    }

def load_data():
    return pd.read_csv('questions.csv', sep=';').to_dict(orient='records')

data = load_data()

class QuizRequest(BaseModel):
    niveau: str = Field(
        description="Niveau du quiz: A (débutant), B (intermédiaire), ou C (avancé)",
        examples=["A", "B", "C"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{"niveau": "B"}]
        }
    }

class QuizResponse(BaseModel):
    quiz: List[dict] = Field(description="Liste des questions du quiz")
    niveau: str = Field(description="Niveau demandé")
    nombre_questions: int = Field(description="Nombre de questions retournées")

@api.post("/generate_quiz", response_model=QuizResponse)
def generate_quiz(request: QuizRequest):
    """
    Génère un quiz de 10 questions aléatoires selon le niveau demandé.
    
    - **niveau A**: Questions de niveau A1 et A2 (débutant)
    - **niveau B**: Questions de niveau B1 et B2 (intermédiaire)
    - **niveau C**: Questions de niveau C1 et C2 (avancé)
    """
    # Map A/B/C to actual levels
    level_map = {
        "A": ["A1", "A2"],
        "B": ["B1", "B2"],
        "C": ["C1", "C2"]
    }
    
    niveau_upper = request.niveau.upper()
    if niveau_upper not in level_map:
        raise HTTPException(
            status_code=400,
            detail=f"Niveau invalide: '{request.niveau}'. Utilisez A, B, ou C."
        )
    
    levels = level_map[niveau_upper]
    filtered_data = [q for q in data if q["niveau"] in levels]
    
    if len(filtered_data) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune question trouvee pour le niveau {request.niveau}."
        )
    
    # Get 10 questions (or less if not enough available)
    count = min(10, len(filtered_data))
    quiz = random.sample(filtered_data, count)
    
    return {"quiz": quiz, "niveau": request.niveau, "nombre_questions": count}

@api.get("/stats")
def get_stats():
    """Retourne les statistiques de la base de questions: total, répartition par niveau et par catégorie."""
    df = pd.DataFrame(data)
    return {
        "total_questions": len(data),
        "par_niveau": df['niveau'].value_counts().to_dict(),
        "par_categorie": df['categorie'].value_counts().to_dict()
    }

class QuestionRequest(BaseModel):
    question: str = Field(min_length=5, max_length=500, description="La question à poser")
    categorie: str = Field(min_length=2, max_length=50, description="Catégorie grammaticale (verbe, adjectif, pronom, etc.)")
    niveau: str = Field(min_length=2, max_length=2, description="Niveau CECRL (A1, A2, B1, B2, C1, C2)")
    reponse: str = Field(min_length=1, max_length=200, description="La bonne réponse (doit correspondre à une des options)")
    reponseA: str = Field(min_length=1, max_length=200, description="Option A")
    reponseB: str = Field(min_length=1, max_length=200, description="Option B")
    reponseC: Optional[str] = Field(default=None, max_length=200, description="Option C (optionnel)")
    reponseD: Optional[str] = Field(default=None, max_length=200, description="Option D (optionnel)")
    commentaire: Optional[str] = Field(default=None, max_length=300, description="Explication ou commentaire")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "question": "Elle ___ au marché hier.",
                "categorie": "verbe",
                "niveau": "A2",
                "reponse": "est allée",
                "reponseA": "a allé",
                "reponseB": "est allée",
                "reponseC": "est allé",
                "reponseD": "a allée",
                "commentaire": "Passé composé avec être"
            }]
        }
    }

@api.post("/create_question")
def create_question(request: QuestionRequest):
    """
    Ajoute une nouvelle question à la base de données.
    
    La question doit contenir au minimum: question, catégorie, niveau, réponse, réponseA, réponseB.
    Les champs réponseC, réponseD et commentaire sont optionnels.
    """
    # Validate level
    valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    if request.niveau.upper() not in valid_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Niveau invalide: '{request.niveau}'. Utilisez: {', '.join(valid_levels)}."
        )
    
    # Validate that reponse matches one of the options
    options = [request.reponseA, request.reponseB, request.reponseC, request.reponseD]
    options = [o for o in options if o is not None]
    if request.reponse not in options:
        raise HTTPException(
            status_code=400,
            detail="La reponse doit correspondre exactement a l'une des options (reponseA, reponseB, reponseC, ou reponseD)."
        )
    
    new_question = {
        "question": request.question,
        "categorie": request.categorie,
        "niveau": request.niveau,
        "reponse": request.reponse,
        "reponseA": request.reponseA,
        "reponseB": request.reponseB,
        "reponseC": request.reponseC,
        "reponseD": request.reponseD,
        "commentaire": request.commentaire
    }

    data.append(new_question)
    df = pd.DataFrame(data)
    df.to_csv('questions.csv', sep=';', index=False)

    return {
        "status": "OK",
        "message": "Question ajoutée avec succès",
        "question": new_question,
        "total_questions": len(data)
    }