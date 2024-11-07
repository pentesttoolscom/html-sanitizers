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

    @GetMapping("/sanitize")
    public String sanitize(
        @RequestParam String html,
        @RequestParam String method
    ) {
        String sanitizedHtml;
        if ("owasp".equals(method)) {
            PolicyFactory policy = new HtmlPolicyBuilder()
                .allowElements("a")
                .allowUrlProtocols("https")
                .allowAttributes("href")
                .onElements("a")
                .requireRelNofollowOnLinks()
                .toFactory();
            sanitizedHtml = policy.sanitize(html);
        } else if ("jsoup".equals(method)) {
            Document doc = Jsoup.parse(html);
            Safelist whitelist = Safelist.basicWithImages();
            whitelist.addTags("a");
            whitelist.addAttributes(":all", "href");
            sanitizedHtml = Jsoup.clean(doc.body().html(), whitelist);
        } else {
            sanitizedHtml = "Invalid method specified.";
        }
        return sanitizedHtml;
    }
}
