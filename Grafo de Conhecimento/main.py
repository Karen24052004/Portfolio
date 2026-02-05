import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

NEO4J_URI = os.getenv("uri")
NEO4J_USER = os.getenv("user")
NEO4J_PASSWORD = os.getenv("password")

GEMINI_API_KEY = os.getenv("gemini_key")

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

neo4j_driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

def embed_query(text: str) -> list:
    return embedding_model.encode(
        [text],
        normalize_embeddings=True
    )[0].tolist()

def search_similar_recipes(query, top_k=5, threshold=0.4):
    query_embedding = embed_query(query)

    with neo4j_driver.session() as session:
        result = session.run(
            """
            WITH $query_embedding AS queryVec
            MATCH (em:Embedding)-[:VETOR_DENSO_DE]->(r:Recipe)
            WITH r, vector.similarity.cosine(queryVec, em.embedding) AS similarity
            WHERE similarity >= $threshold
            RETURN r.recipe_name AS recipe_name, similarity
            ORDER BY similarity DESC
            LIMIT $top_k
            """,
            query_embedding=query_embedding,
            threshold=threshold,
            top_k=top_k
        )

        return result.data()

def get_recipe_details(recipe_name):
    query = """
    SELECT
        recipe_name,
        cuisine,
        ingredients,
        dietary_restrictions,
        calories_per_serving
    FROM receitas
    WHERE recipe_name = :name
    """

    with engine.connect() as conn:
        return conn.execute(
            text(query),
            {"name": recipe_name}
        ).fetchone()

def ask_gemini(user_query, recipes):
    context = ""

    for r in recipes:
        context += f"""
Recipe: {r['recipe_name']}
Cuisine: {r['cuisine']}
Ingredients: {r['ingredients']}
Dietary: {r['dietary_restrictions']}
Calories: {r['calories_per_serving']}
---
"""

    prompt = f"""
You are a professional cooking assistant.

User request:
"{user_query}"

Based ONLY on the recipes below:
- Recommend the best recipe(s)
- Explain why they match the ingredients
- Suggest small adaptations if needed
- Do NOT invent recipes

Recipes:
{context}
"""

    response = gemini_model.generate_content(prompt)
    return response.text

sentence = input(
    "\n🍳 Enter ingredients or a description: "
).strip()

results = search_similar_recipes(sentence)

if not results:
    print("\n❌ No similar recipes found.")
else:
    print("\n🔥 Top matching recipes:\n")

    recipes_for_ai = []

    for r in results:
        details = get_recipe_details(r["recipe_name"])

        if details:
            print(f"🍽 {details.recipe_name}")
            print(f"   Cuisine: {details.cuisine}")
            print(f"   Ingredients: {details.ingredients}")
            print(f"   Dietary: {details.dietary_restrictions}")
            print(f"   Calories: {details.calories_per_serving}")
            print(f"   Similarity: {round(r['similarity'], 3)}")
            print("-" * 50)

            recipes_for_ai.append({
                "recipe_name": details.recipe_name,
                "cuisine": details.cuisine,
                "ingredients": details.ingredients,
                "dietary_restrictions": details.dietary_restrictions,
                "calories_per_serving": details.calories_per_serving
            })

    use_ai = input(
        "\n🤖 Do you want an AI recommendation based on these recipes? (y/n): "
    ).strip().lower()

    if use_ai == "y":
        print("\n🍳 AI Recommendation:\n")
        print(ask_gemini(sentence, recipes_for_ai))
    else:
        print("\n👍 OK! Search completed without AI.")
