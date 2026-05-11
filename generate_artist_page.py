import json
import os
import re

# --- Configurazione ---
TEMPLATE_PATH = "_templates/artist_template.html"
DATA_PATH = "_templates/artist_data_example.json"
OUTPUT_DIR = "." # Genera i file nella root del progetto
# -----------------------

def load_template(template_path):
    """Carica il contenuto del template HTML."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERRORE: Template non trovato al percorso: {template_path}")
        return None

def load_data(data_path):
    """Carica i dati dell'artista dal file JSON."""
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERRORE: File dati non trovato al percorso: {data_path}")
        return None
    except json.JSONDecodeError:
        print(f"ERRORE: Formato JSON non valido nel file: {data_path}")
        return None

def generate_html_page(template, data):
    """Sostituisce tutti i placeholder nel template con i dati forniti."""
    if not template or not data:
        return None

    # 1. Sostituzione dei placeholder globali
    html_content = template
    
    # Sostituzioni base
    html_content = html_content.replace("[ARTIST_NAME]", data.get("artist_name", "Nome Artista"))
    html_content = html_content.replace("[ARTIST_SLOGAN]", data.get("content", {}).get("sub_it", "Slogan generico"))
    html_content = html_content.replace("[ARTIST_SLOGAN_EN]", data.get("content", {}).get("sub_en", "Generic Slogan"))
    html_content = html_content.replace("[ARTIST_SLUG]", data.get("slug", "artista-generato"))
    html_content = html_content.replace("[ARTIST_CLASS]", data.get("class", "artist-default"))
    
    # Sostituzioni Immagini
    html_content = html_content.replace("[ARTIST_IMAGE_WEBP]", data["images"]["hero_webp"])
    html_content = html_content.replace("[ARTIST_IMAGE_JPG]", data["images"]["hero_jpg"])
    html_content = html_content.replace("[ARTIST_PRESSKIT_WEBP]", data["images"]["presskit_webp"])
    html_content = html_content.replace("[ARTIST_PRESSKIT_JPG]", data["images"]["presskit_jpg"])
    
    # Sostituzioni Contenuti
    html_content = html_content.replace("[PARAGRAFO INTRODUZIONE ITALIANO]", data["content"]["intro_it"])
    html_content = html_content.replace("[INTRO PARAGRAPH ENGLISH]", data["content"]["intro_en"])
    html_content = html_content.replace("[PARAGRAFO SUB ITALIANO]", data["content"]["sub_it"])
    html_content = html_content.replace("[SUB PARAGRAPH ENGLISH]", data["content"]["sub_en"])
    
    # Sostituzioni Servizi (semplificato per l'esempio)
    service_html = f"""
          <article class="service-item">
            <h3 data-lang="it">{data["services"][0]["title_it"]}</h3>
            <p data-lang="it">{data["services"][0]["description_it"]}</p>
          </article>"""
    html_content = html_content.replace("<!-- Qui si possono aggiungere altri servizi in modo standardizzato -->", service_html)

    # Sostituzioni Press Kit
    html_content = html_content.replace("[ARTIST_TAG]", data["tag"])
    html_content = html_content.replace("[TAG]", data["tag"])
    html_content = html_content.replace("[DESCRIZIONE BREVE PER PRESS KIT]", data["presskit"]["descrizione_breve_it"])
    
    return html_content

def main():
    """Funzione principale per generare la pagina."""
    print("--- Avvio Generazione Pagina Artista ---")
    
    # 1. Carica i dati e il template
    template = load_template(TEMPLATE_PATH)
    data = load_data(DATA_PATH)

    if not template or not data:
        print("Impossibile procedere a causa di errori di caricamento.")
        return

    # 2. Genera il contenuto finale
    final_html = generate_html_page(template, data)

    if final_html:
        # 3. Salva il file nella root del progetto
        output_filename = f"{data['slug']}.html"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        
        print(f"\n✅ SUCCESSO: Pagina generata e salvata come '{output_filename}' nella root del progetto.")
        print("Ricorda di aggiornare anche i link nel file index.html e nel menu di navigazione.")

if __name__ == "__main__":
    main()