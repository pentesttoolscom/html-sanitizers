package main

import (
	"fmt"
	"html/template"
	"net/http"

	"github.com/microcosm-cc/bluemonday"
)

func safeHTML(s string) template.HTML {
	return template.HTML(s)
}

func indexHandler(w http.ResponseWriter, r *http.Request) {
	html := r.URL.Query().Get("html")
	var sanitizedHTML string

	if html != "" {
		p := bluemonday.UGCPolicy()

		sanitizedHTML = p.Sanitize(html)
	}

	tmpl, err := template.New("index.html").Funcs(template.FuncMap{
		"safeHTML": safeHTML,
	}).ParseFiles("index.html")
	if err != nil {
		http.Error(w, "Error parsing template", http.StatusInternalServerError)
		return
	}

	data := map[string]string{
		"SanitizedHTML": sanitizedHTML,
	}

	if err := tmpl.Execute(w, data); err != nil {
		http.Error(w, "Error rendering template", http.StatusInternalServerError)
	}
}

func main() {
	http.HandleFunc("/", indexHandler)

	fmt.Println("Starting server at :80")
	if err := http.ListenAndServe(":80", nil); err != nil {
		fmt.Printf("Error starting server: %s\n", err)
	}
}
