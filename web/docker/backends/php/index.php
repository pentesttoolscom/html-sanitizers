<?php 
// Require composer autoloader
require __DIR__ . '/vendor/autoload.php';

use TYPO3\HtmlSanitizer\Builder\CommonBuilder;
use Symfony\Component\HtmlSanitizer\HtmlSanitizer;
use Symfony\Component\HtmlSanitizer\HtmlSanitizerConfig;

// Create Router instance
$router = new \Bramus\Router\Router();

// Define routes
$router->get('typo3', function() {
    $payload = (string)($_GET['text'] ?? '');
    if (empty($payload)) {
        $payload = 'No text given';
    }

    $sanitizer = (new CommonBuilder())->build();
    echo $sanitizer->sanitize($payload);
});

$router->get('html-purifier', function() {
    $payload = (string)($_GET['text'] ?? '');
    if (empty($payload)) {
        $payload = 'No text given';
    }

    $config = HTMLPurifier_Config::createDefault();
    $purifier = new HTMLPurifier($config);
    echo $purifier->purify($payload);
});

$router->get("symfony-sanitizer", function() {
    $htmlSanitizer = new HtmlSanitizer(
        (new HtmlSanitizerConfig())->allowSafeElements()
    );
    $payload = (string)($_GET['text'] ?? '');
    if (empty($payload)) {
        $payload = 'No text given';
    }
    echo $htmlSanitizer->sanitize($payload);
});

// Run it!
$router->run();
?>