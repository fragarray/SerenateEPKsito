<?php
/**
 * upload.php – AltraMarea Produzioni
 * Receiver per upload immagini dall'admin.
 *
 * CONFIGURAZIONE:
 *   1. Cambia UPLOAD_TOKEN con una stringa segreta a tua scelta.
 *      Lo stesso token deve essere impostato in UPLOAD_CFG.token in admin.html.
 *   2. Per maggiore sicurezza, aggiungi in .htaccess:
 *         <Files "upload.php">
 *           Order Deny,Allow
 *           Deny from all
 *           Allow from TUO_IP
 *         </Files>
 */

// ── CONFIG ────────────────────────────────────────────────────────
define('UPLOAD_TOKEN', 'tokensegretoaltramareaproduzioni'); // token segreto condiviso con admin.html
define('IMG_DIR',      __DIR__ . '/img/');
define('MAX_BYTES',    12 * 1024 * 1024);       // 12 MB
define('ALLOWED_MIME', ['image/jpeg', 'image/webp', 'image/png']);
define('ALLOWED_EXT',  ['jpg', 'jpeg', 'webp', 'png']);
// ─────────────────────────────────────────────────────────────────

header('Content-Type: application/json; charset=utf-8');

// Blocca richieste non-POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit(json_encode(['ok' => false, 'error' => 'Metodo non consentito.']));
}

function fail(string $msg, int $code = 400): never {
    http_response_code($code);
    echo json_encode(['ok' => false, 'error' => $msg]);
    exit;
}

// ── Verifica token ────────────────────────────────────────────────
$token = $_POST['token'] ?? '';
if (!hash_equals(UPLOAD_TOKEN, $token)) {
    fail('Accesso non autorizzato.', 403);
}

$action = $_POST['action'] ?? 'upload';

// ══════════════════════════════════════════════════════════════════
// ACTION: delete
// ══════════════════════════════════════════════════════════════════
if ($action === 'delete') {
    $rawPath = $_POST['path'] ?? '';

    // Accetta solo path nella forma "img/filename.ext"
    if (!preg_match('/^img\/[a-z0-9_\-]+\.[a-z]{3,4}$/i', $rawPath)) {
        fail('Path non valido.');
    }

    $realTarget = realpath(__DIR__ . '/' . $rawPath);
    $imgDir     = realpath(IMG_DIR);

    // Sicurezza: verifica che il file sia davvero dentro img/
    if ($realTarget === false || $imgDir === false || strpos($realTarget, $imgDir) !== 0) {
        fail('Path non consentito.');
    }

    if (!file_exists($realTarget)) {
        // File già assente — consideriamo comunque OK
        echo json_encode(['ok' => true, 'note' => 'File non trovato (già eliminato).']);
        exit;
    }

    if (!unlink($realTarget)) {
        fail('Impossibile eliminare il file. Controlla i permessi.');
    }

    echo json_encode(['ok' => true, 'deleted' => $rawPath]);
    exit;
}

// ══════════════════════════════════════════════════════════════════
// ACTION: upload (default)
// ══════════════════════════════════════════════════════════════════

// ── Verifica file ─────────────────────────────────────────────────
if (empty($_FILES['file'])) {
    fail('Nessun file ricevuto.');
}

$f = $_FILES['file'];

if ($f['error'] !== UPLOAD_ERR_OK) {
    $errors = [
        UPLOAD_ERR_INI_SIZE   => 'File supera upload_max_filesize di PHP.',
        UPLOAD_ERR_FORM_SIZE  => 'File supera MAX_FILE_SIZE del form.',
        UPLOAD_ERR_PARTIAL    => 'Upload parziale.',
        UPLOAD_ERR_NO_FILE    => 'Nessun file selezionato.',
        UPLOAD_ERR_NO_TMP_DIR => 'Cartella temporanea mancante.',
        UPLOAD_ERR_CANT_WRITE => 'Impossibile scrivere su disco.',
        UPLOAD_ERR_EXTENSION  => 'Upload bloccato da estensione PHP.',
    ];
    fail($errors[$f['error']] ?? 'Errore upload: codice ' . $f['error']);
}

if ($f['size'] > MAX_BYTES) {
    fail('File troppo grande (max 12 MB).');
}

// ── Verifica MIME reale (non quella dichiarata dal client) ─────────
if (!function_exists('finfo_open')) {
    fail('Estensione finfo non disponibile sul server.');
}
$finfo = new finfo(FILEINFO_MIME_TYPE);
$mime  = $finfo->file($f['tmp_name']);
if (!in_array($mime, ALLOWED_MIME, true)) {
    fail('Tipo file non consentito: ' . $mime);
}

// ── Verifica estensione ───────────────────────────────────────────
$ext = strtolower(pathinfo($f['name'], PATHINFO_EXTENSION));
if (!in_array($ext, ALLOWED_EXT, true)) {
    fail('Estensione non consentita: ' . $ext);
}

// ── Sanifica il nome file ─────────────────────────────────────────
$base     = pathinfo($f['name'], PATHINFO_FILENAME);
$base     = preg_replace('/[^a-z0-9_\-]/i', '_', $base);
$base     = strtolower(trim($base, '_'));
$base     = substr($base ?: 'img', 0, 60);
$filename = $base . '_' . time() . '.' . $ext;
$dest     = IMG_DIR . $filename;

// ── Controlla che la cartella esista ─────────────────────────────
if (!is_dir(IMG_DIR)) {
    fail('Cartella img/ non trovata sul server. Creala via FTP/cPanel.');
}

// ── Sposta il file ────────────────────────────────────────────────
if (!move_uploaded_file($f['tmp_name'], $dest)) {
    fail('Impossibile salvare il file. Controlla i permessi della cartella img/.');
}

// ── Risposta successo ─────────────────────────────────────────────
echo json_encode([
    'ok'   => true,
    'path' => 'img/' . $filename,
    'name' => $filename,
    'size' => $f['size'],
]);
