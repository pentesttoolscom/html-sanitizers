using Ganss.Xss;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/html-sanitizer", (HttpRequest req) => {
    var text = req.Query["text"].ToString();
    if (string.IsNullOrEmpty(text)) {
        return Results.Text("No text given", "plain/text");
    }
    if (string.IsNullOrEmpty(text)) {
        return Results.Text("No text given", "plain/text");
    }
    var sanitizer = new HtmlSanitizer();
    try
    {
        var sanitized = sanitizer.Sanitize(text);
        return Results.Text(sanitized, contentType: "text/html");
    }
    catch (Exception ex)
    {
        return Results.Text(ex.ToString(), contentType: "text/html",statusCode: 500);
    }
});

app.Run();
