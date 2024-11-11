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

func bluemondayHandler(w http.ResponseWriter, r *http.Request) {
	text := r.URL.Query().Get("text")
	var sanitizedHTML string

	if text != "" {
		p := bluemonday.UGCPolicy()

		sanitizedHTML = p.Sanitize(text)
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
	http.HandleFunc("/bluemonday", bluemondayHandler)

	fmt.Println("Starting server at :80")
	if err := http.ListenAndServe(":80", nil); err != nil {
		fmt.Printf("Error starting server: %s\n", err)
	}
}
