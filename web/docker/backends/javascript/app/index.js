const express = require('express');
const app = express();
const htmlSanitize = require('sanitize-html');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const createDOMPurify = require('dompurify');

const window = new JSDOM('').window;
const DOMPurify = createDOMPurify(window);

app.get('/sanitize-html', (req, res) => {
  const text = req.query.text;

  if (!text) {
    res.set('Content-Type', 'text/plain');
    return res.send('No text given');
  }
  console.log("Received: ", text)
  const sanitizedText = htmlSanitize(text);

  res.set('Content-Type', 'text/html');
  res.send(sanitizedText);
});

app.get('/dompurify', (req, res) => {
  const text = req.query.text;

  if (!text) {
    res.set('Content-Type', 'text/plain');
    return res.send('No text given');
  }
  console.log("Received: ", text)
  const sanitizedText = DOMPurify.sanitize(text);
  res.set('Content-Type', 'text/html');
  res.send(sanitizedText);
});

app.listen(8080, () => {
  console.log('Server started on port 8080');
});

