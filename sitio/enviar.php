<?php
/* Vinos Gallegos Pousada · formulario de solicitud de tarifa (y «Que me llamen», si la web lo lleva).
   Antispam sin captcha: campo trampa con nombre sin sentido (contacto_alt), tiempo en la página y sin enlaces en el mensaje.
   «t» lo rellena main.js al enviar: milisegundos que lleva la página abierta. Un envío demasiado rápido (o con la página
   abierta más de 24 h) NO se descarta: se envía igual, marcado como SOSPECHOSO en el asunto. Solo se descarta la trampa
   rellena (un robot). Ningún descarte silencioso (Dani C-02): cada rechazo vuelve con su motivo y queda en el registro.
   Buzón de destino: info@vinospousada.es · aviso corto a un segundo buzón:  (vacío = sin aviso).
   Registro sin datos personales (fecha, resultado, motivo, página) en ../solicitudes-web.log, fuera de la carpeta
   pública, si el hosting deja escribir ahí. */
header('X-Robots-Tag: noindex');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: /contacto/'); exit; }
$c = function ($k, $max) { return trim(mb_substr(strip_tags((string)($_POST[$k] ?? '')), 0, $max)); };
$tipo = ($_POST['tipo'] ?? '') === 'llamada' ? 'llamada' : 'contacto';
$pagina = $c('pagina', 120);
if (!preg_match('#^/[a-z0-9\-/]*$#', $pagina) || strpos($pagina, '//') !== false) { $pagina = '/'; }
$nombre = $c('nombre', 80); $telefono = $c('telefono', 20); $negocio = $c('negocio', 80); $tipo_negocio = $c('tipo_negocio', 30);
$municipio = $c('municipio', 60); $mensaje = $c('mensaje', 2000);
$trampa = (string)($_POST['contacto_alt'] ?? ''); $t = (int)($_POST['t'] ?? 0);
/* Teléfono: se admite +34, espacios, puntos, guiones y paréntesis; se exigen de 9 a 15 cifras */
$solo = preg_replace('/[^0-9+]/', '', $telefono); $cifras = strlen(preg_replace('/\D/', '', $solo));
$motivo = '';
if ($trampa !== '') { $motivo = 'trampa'; }
elseif ($nombre === '') { $motivo = 'nombre'; }
elseif ($cifras < 9 || $cifras > 15 || strpos($solo, '+') > 0) { $motivo = 'telefono'; }
elseif ($tipo === 'contacto' && $negocio === '') { $motivo = 'negocio'; }
elseif ($tipo === 'contacto' && $tipo_negocio === '') { $motivo = 'tipo_negocio'; }
elseif (preg_match('#https?://|www\.#i', $mensaje)) { $motivo = 'enlaces'; }
$sospechoso = ($t < 3000 || $t > 86400000);
if ($tipo === 'llamada') { $vuelta = $pagina; $clave = 'llamada'; $ancla = '#te-llamamos'; $ancla_ko = '#te-llamamos'; }
else { $vuelta = ($pagina !== '/' && $pagina !== '') ? $pagina : '/contacto/'; $clave = 'enviado'; $ancla = '#form-ok'; $ancla_ko = '#form-error'; }
$registro = function ($linea) { @file_put_contents(dirname(__DIR__) . '/solicitudes-web.log', date('c') . ' ' . $linea . "\n", FILE_APPEND | LOCK_EX); };
if ($motivo === 'trampa') { $registro("robot pagina=$pagina"); header('Location: ' . $vuelta . '?' . $clave . '=1' . $ancla); exit; } /* a los robots no se les da pista */
if ($motivo !== '') { $registro("rechazado motivo=$motivo pagina=$pagina"); header('Location: ' . $vuelta . '?' . $clave . '=0&motivo=' . $motivo . $ancla_ko); exit; }
$para = 'info@vinospousada.es'; $aviso = '';
$marca = $sospechoso ? 'SOSPECHOSO · ' : '';
$interes = preg_match('/me interesa:\s*([^.\n]{1,80})/iu', $mensaje, $mi) ? trim($mi[1]) : '';
$segundos = $t > 0 ? round($t / 1000) . ' s con la página abierta' : 'tiempo en la página desconocido';
if ($tipo === 'llamada') {
  $asunto = '=?UTF-8?B?' . base64_encode($marca . 'QUE ME LLAMEN · ' . $nombre . ' · ' . $telefono) . '?=';
  $cuerpo = "Petición de llamada desde la web.\n\nNombre: $nombre\nTeléfono: $telefono\nPágina: https://vinospousada.es$pagina\n$segundos\n";
} else {
  $asunto = '=?UTF-8?B?' . base64_encode($marca . 'SOLICITUD DE TARIFA · ' . $negocio . ' (' . $tipo_negocio . ') · ' . $nombre . ' · ' . $telefono . ($interes !== '' ? ' · ' . $interes : '')) . '?=';
  $cuerpo = "Solicitud de tarifa desde la web.\n\nNombre: $nombre\nNegocio: $negocio\nTipo de negocio: $tipo_negocio\nTeléfono: $telefono\n"
    . ($municipio !== '' ? "Municipio: $municipio\n" : '') . ($interes !== '' ? "Le interesa: $interes\n" : '')
    . "\nMensaje:\n" . ($mensaje !== '' ? $mensaje : '(sin mensaje)') . "\n\nPágina: https://vinospousada.es$pagina\n$segundos"
    . ($sospechoso ? " (marcada como sospechosa: puede ser un robot; si los datos tienen sentido, es una solicitud real)" : '')
    . "\n-- Enviado desde vinospousada.es/contacto/\n";
}
$cab = "From: Web Vinos Gallegos Pousada <web@vinospousada.es>\r\nReply-To: Web Vinos Gallegos Pousada <web@vinospousada.es>\r\nContent-Type: text/plain; charset=UTF-8\r\n";
$enviado = @mail($para, $asunto, $cuerpo, $cab);
if ($aviso !== '' && $aviso !== $para) {
  /* Aviso corto al segundo buzón (el móvil lo muestra entero en la notificación): quién, qué tipo de local y el teléfono */
  $asunto2 = '=?UTF-8?B?' . base64_encode($marca . 'Aviso · solicitud de tarifa en la web · ' . ($tipo === 'llamada' ? $nombre : $negocio)) . '?=';
  $cuerpo2 = "Ha entrado una solicitud en https://vinospousada.es.\n" . ($tipo === 'llamada' ? "Nombre: $nombre" : "Negocio: $negocio ($tipo_negocio)") . "\nTeléfono: $telefono\n"
    . ($interes !== '' ? "Le interesa: $interes\n" : '') . "\nEl correo completo " . ($enviado ? "está en $para." : "NO se ha podido entregar en $para: llame a este teléfono.") . "\n";
  @mail($aviso, $asunto2, $cuerpo2, $cab);
}
$registro(($enviado ? 'enviado' : 'FALLO-mail') . " tipo=$tipo pagina=$pagina tipo_negocio=$tipo_negocio" . ($sospechoso ? ' sospechoso' : ''));
header('Location: ' . $vuelta . '?' . $clave . '=' . ($enviado ? '1' . $ancla : '0&motivo=envio' . $ancla_ko));
