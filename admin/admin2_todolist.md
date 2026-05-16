# Admin 2.0 — Todolist di sviluppo
> Versione editor visuale con drag&drop e toolbar contestuale stile Canva  
> Basata sull'analisi di `admin.html` v1 · Aggiornata il 15/05/2026

---

## Decisioni architetturali (già confermate)

| Aspetto | Scelta |
|---|---|
| Preview | **Iframe interattivo** — JS/CSS iniettati nell'iframe via `postMessage` |
| Granularità blocchi | **Qualsiasi elemento** — paragrafi singoli, foto individuali, video, sezioni |
| Toolbar contestuale | Sostituisci · Elimina · Duplica · Sposta su/giù · Modifica inline · Cambia variante |
| Tipi di blocco | Foto · Video YouTube · Paragrafo testo · Sezione titolo+testo · Galleria · Scheda tecnica · Separatore |
| Formato JSON | **Nuovo formato v2** (non compatibile con v1, ma con migrazione assistita) |

---

## FASE 0 — Setup e struttura file

- [ ] **0.1** Copiare `admin.html` → `admin2.html` come base di partenza
- [ ] **0.2** Definire il nuovo schema dati JSON v2 (`block[]` array con `type`, `id`, `order`, `data{}`)
- [ ] **0.3** Scrivere un adattatore di migrazione `migrateV1toV2(jsonV1)` per aprire progetti v1

---

## FASE 1 — Modello dati a blocchi

### 1.1 Blocchi standard (portati da v1)
Ogni blocco ha struttura `{ id, type, order, data, variant }`:

- [ ] `block:identity` — nome artista, slug, meta, palette, header type *(dati globali, non riordinabili)*
- [ ] `block:hero` — immagine hero con varianti dimensione
- [ ] `block:intro` — lead paragraph + sub paragraphs (bilingue)
- [ ] `block:photo` — foto singola full-width con alt text
- [ ] `block:video` — YouTube embed con titolo bilingue
- [ ] `block:text-section` — sezione con titolo + corpo (bilingue, opzione sfondo alt)
- [ ] `block:specs` — scheda tecnica (tabella dati tecnici)
- [ ] `block:contacts` — footer contatti + social

### 1.2 Blocchi nuovi (non presenti in v1)
- [ ] `block:gallery` — griglia 2-3 colonne con foto multiple
- [ ] `block:separator` — spazio vuoto / divisore visivo con altezza configurabile

### 1.3 Renderer
- [ ] Funzione `renderBlock(block, lang)` → HTML string per ciascun tipo
- [ ] Funzione `renderPage(blocks, lang)` → pagina completa (sostituisce `buildHTML()`)
- [ ] Funzione `buildCardHTML(blocks)` → card per index.html (come v1)

---

## FASE 2 — Pannello sinistro: form editor

> L'obiettivo è che il form segua l'ordine dei blocchi nel canvas, non un ordine fisso.

- [ ] **2.1** Rimpiazzare le 8 sezioni fisse con un elenco dinamico di **pannelli-blocco** che rispecchiano l'ordine attuale del canvas
- [ ] **2.2** Ogni pannello-blocco ha: header collassabile con nome tipo + drag handle + icone azione (elimina, duplica)
- [ ] **2.3** "Sezione Globale" separata in cima per i campi non riordinabili (identità, palette, header)
- [ ] **2.4** Pulsante "+ Aggiungi blocco" in fondo alla lista con menu a scelta tipo blocco
- [ ] **2.5** Mantenere tutte le funzionalità v1: upload immagini, lang-tabs, slug auto, contatori meta

---

## FASE 3 — Iframe interattivo (canvas)

> Questa è la parte più delicata. Tutta la comunicazione avviene via `postMessage`.

### 3.1 Infrastruttura postMessage
- [ ] Definire il protocollo messaggi: `{ cmd, payload }` (cmds: `init`, `updateBlock`, `setMode`, `highlightBlock`, `reorderBlocks`)
- [ ] Script `preview-bridge.js` da iniettare nell'iframe ad ogni rebuild
- [ ] Funzione `sendToPreview(cmd, payload)` lato admin

### 3.2 Modalità EDITOR nell'iframe
- [ ] Quando l'iframe riceve `setMode:'editor'`, aggiunge classe `.editor-mode` al body
- [ ] In `.editor-mode`: ogni blocco riconoscibile (`[data-block-id]`) diventa draggable
- [ ] Highlight hover con bordo colorato + ombra (niente interferenza col CSS reale)
- [ ] Cursore `grab` sui blocchi, `grabbing` durante il trascinamento

### 3.3 Drag & Drop nell'iframe
- [ ] Implementare drag&drop con **HTML5 Drag API** oppure libreria leggera (SortableJS via CDN)
- [ ] Ogni blocco nel HTML generato riceve attributo `data-block-id="<uuid>"`
- [ ] Al drop: iframe invia `postMessage({ cmd:'reorder', newOrder:[id,...] })` al parent
- [ ] Parent aggiorna il modello dati e rigenera il form sinistro nell'ordine corretto
- [ ] Animazione di riposizionamento fluida (CSS transition su `transform`)

### 3.4 Aggiornamento parziale (performance)
- [ ] Invece di rebuilddare tutta la pagina ad ogni modifica, implementare `patchBlock(id, newHTML)`
- [ ] Debounce aggiornamenti: 400ms (come v1) per input testo, 0ms per drag&drop

---

## FASE 4 — Toolbar contestuale (stile Canva)

### 4.1 Struttura toolbar
- [ ] Elemento `.block-toolbar` iniettato nell'iframe in `.editor-mode`
- [ ] Posizionamento: appare in alto a destra del blocco hovered (position absolute calcolata)
- [ ] Scompare con delay 200ms sull'uscita mouse (per permettere click sulle icone)
- [ ] Z-index sopra tutto, pointer-events solo sulle icone

### 4.2 Icone toolbar (SVG inline, stile coerente con admin)
- [ ] **↑ Sposta su** — riordina il blocco di una posizione verso l'alto
- [ ] **↓ Sposta giù** — riordina il blocco di una posizione verso il basso
- [ ] **⊕ Cambia tipo** — apre mini-menu con i tipi disponibili (icone + label)
- [ ] **◧ Cambia variante** — apre mini-menu varianti (es. foto: full-width / incorniciata / 50% + testo)
- [ ] **⎘ Duplica** — duplica il blocco con nuovo ID, inserito immediatamente sotto
- [ ] **✏ Modifica inline** — attiva editing diretto nel preview (vedi fase 5)
- [ ] **✕ Elimina** — rimuove il blocco (con conferma via tooltip "Clicca di nuovo per confermare")

### 4.3 Sincronizzazione form ↔ canvas
- [ ] Click su blocco nel canvas → panel corrispondente nel form si espande e fa scroll in vista
- [ ] Modifica nel form → blocco corrispondente nel canvas viene highlighted brevemente (flash)

---

## FASE 5 — Editing inline nel preview

> La funzione più complessa. Si attiva solo per tipi di testo.

- [ ] **5.1** Per `block:intro`, `block:text-section`: click su paragrafo → `contenteditable="true"` attivato
- [ ] **5.2** Barra di formattazione mini sopra il testo in editing (grassetto, corsivo, link)
- [ ] **5.3** Al blur → il testo modificato viene mandato al parent via `postMessage({ cmd:'inlineEdit', blockId, field, value })`
- [ ] **5.4** Parent aggiorna il modello dati e il campo nel form sinistro
- [ ] **5.5** Per `block:photo`: click sull'immagine → apre dialog "Sostituisci immagine" (URL o upload)
- [ ] **5.6** Per `block:video`: click sul placeholder video → apre inline input per YouTube ID

---

## FASE 6 — Funzioni ereditate da v1 (da portare intatte)

- [ ] **6.1** `saveProject()` / `openProject()` → adattati al formato JSON v2
- [ ] **6.2** `generateAndDownload()` → genera ZIP con HTML bilingue + card + presskit
- [ ] **6.3** Upload immagini via `upload.php` (stesso endpoint, stesso token)
- [ ] **6.4** `detachPreview()` / `reattachPreview()` → finestra separata
- [ ] **6.5** Palette colori (preset + custom) con swatch live
- [ ] **6.6** Scroll-spy: editing su un blocco → preview scrolla al blocco corrispondente
- [ ] **6.7** `loadSiteCSS()` → CSS del sito iniettato nell'iframe per preview fedele
- [ ] **6.8** Adattatore migrazione: pulsante "Apri progetto v1" che legge `.json` v1 e converte

---

## FASE 7 — UX e rifinitura

- [ ] **7.1** Indicatore visivo "editor mode attivo" nella topbar del preview
- [ ] **7.2** Pulsante toggle per disattivare editor mode e vedere preview pulita
- [ ] **7.3** Undo/Redo — stack di stati (almeno 20 step), shortcut Ctrl+Z / Ctrl+Y
- [ ] **7.4** Indicatore "modifiche non salvate" nel header (pallino arancione)
- [ ] **7.5** Autosave su `localStorage` ogni 60s (ripristino dopo chiusura accidentale)
- [ ] **7.6** Responsive nel form: su schermi < 1200px la sidebar si collassa (come v1)
- [ ] **7.7** Cursore drag handle visibile solo su hover del pannello-blocco nel form sinistro
- [ ] **7.8** Animazione di riordino anche nel form sinistro (i pannelli si spostano con CSS transition)

---

## Ordine consigliato di sviluppo

```
FASE 0 → FASE 1 (modello dati) → FASE 2 (form base) → FASE 3 (iframe base, no toolbar)
→ FASE 6 (funzioni v1 portate) → FASE 4 (toolbar) → FASE 5 (inline edit) → FASE 7 (rifinitura)
```

Lavorare in questo ordine permette di avere una versione funzionante (anche senza toolbar) dopo la Fase 3+6, e di aggiungere le funzioni avanzate incrementalmente.

---

## Note tecniche / rischi

| Rischio | Mitigazione |
|---|---|
| `postMessage` tra iframe e parent: sicurezza origin | Verificare sempre `event.origin` nell'event listener |
| SortableJS nell'iframe: conflitti CSS | Isolare gli stili del drag in un `<style id="editor-overlay">` separato |
| Editing inline con `contenteditable`: sincronizzazione complicata | Limitare a elementi foglia (paragrafi singoli), mai su container |
| Performance con molti blocchi | `patchBlock()` parziale + `requestAnimationFrame` per aggiornamenti DOM |
| Retrocompatibilità v1 non richiesta | Aggiungere warning chiaro quando si apre un `.json` v1 con migrazione automatica |
