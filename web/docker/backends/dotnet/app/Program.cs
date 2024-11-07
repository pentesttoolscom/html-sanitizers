using Ganss.Xss;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapPost("/html-sanitizer", async (HttpRequest req) => {
    var form = await req.ReadFormAsync();
    var text = form["text"].ToString();
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
