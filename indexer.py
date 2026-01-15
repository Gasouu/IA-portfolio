import os
import glob
from dotenv import load_dotenv
from upstash_vector import Index

load_dotenv(override=True)

index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"),
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
)

def index_data():
    print("🔄 Début de l'indexation...")
    
    files = glob.glob("data/*.md")
    if not files:
        print("❌ Aucun fichier trouvé dans le dossier 'data/'. Crée un fichier .md (ex: profil.md).")
        return

    vectors = []
    print(f"📄 Fichiers trouvés : {files}")

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        chunks = content.split("##")
        
        for i, chunk in enumerate(chunks):
            text = chunk.strip()
            if len(text) > 10: 
                if i > 0: 
                    text = "## " + text
                
                vectors.append({
                    "id": f"{os.path.basename(file_path)}-{i}",
                    "data": text,
                    "metadata": {"source": os.path.basename(file_path)}
                })

    if vectors:
        try:
            batch_size = 10
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                index.upsert(vectors=batch)
            
            print(f"✅ Succès ! {len(vectors)} sections ont été indexées dans Upstash.")
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi : {e}")
    else:
        print("⚠️ Aucune section valide trouvée (fichiers vides ou trop courts ?).")

if __name__ == "__main__":
    index_data()