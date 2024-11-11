package com.example.htmlsanitizer;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.safety.Safelist;
import org.owasp.html.HtmlPolicyBuilder;
import org.owasp.html.PolicyFactory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class SanitizerController {

    @GetMapping("/owasp")
    public String owasp(@RequestParam String text) {
        String sanitizedHtml;
        PolicyFactory policy = new HtmlPolicyBuilder()
            .allowElements("a")
            .allowUrlProtocols("https")
            .allowAttributes("href")
            .onElements("a")
            .requireRelNofollowOnLinks()
            .toFactory();
        sanitizedHtml = policy.sanitize(text);
        return sanitizedHtml;
    }

    @GetMapping("/jsoup")
    public String jsoup(@RequestParam String text) {
        String sanitizedHtml;
        Document doc = Jsoup.parse(text);
        Safelist whitelist = Safelist.basicWithImages();
        whitelist.addTags("a");
        whitelist.addAttributes(":all", "href");
        sanitizedHtml = Jsoup.clean(doc.body().html(), whitelist);
        return sanitizedHtml;
    }
}
