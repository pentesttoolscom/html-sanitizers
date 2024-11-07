# BlueMonday
## Code import pattern

To import the `bluemonday` library, we can use the following syntax. When importing packages in Go, we need to specify the full path of the package we want to import:

```go
import (
	"github.com/microcosm-cc/bluemonday"
)
```

In order to find any reference to `bluemonday` usage, we can just search for the `github.com/microcosm-cc/bluemonday` string in the `.go` files.
## Policy Building

To determine which HTML elements and attributes are considered safe for a scenario, we have to create a new policy and add elements to a policy:

```go
p := bluemonday.NewPolicy()
p.AllowElements("b", "strong")
```

A common XSS code pattern will include the elements that allow code to be executed by the client or third party content. It should contain one of the following elements:

```go
p.AllowElements("script", "style", "iframe", "object", "embed", "base")
```

[!] If the `bluemonday.UGCPolicy()`  or `bluemonday.StrictPolicy()` are used, then there is no risk, being two safe policies that does not allow unsafe elements and attributes.

[I] The policy can include regexes, representing another attack vector.

Code example that sanitise the `html` variable and allows the `href` and `a` tags:

```go
package main

import (
	"fmt"
	"github.com/microcosm-cc/bluemonday"
)

func main() {
	p := bluemonday.NewPolicy()

	// Require URLs to be parseable by net/url.Parse and either:
	//   mailto: http:// or https://
	p.AllowStandardURLs()

	// We only allow <p> and <a href="">
	p.AllowAttrs("href").OnElements("a")
	p.AllowElements("p")

	html := p.Sanitize(
		`<a onblur="alert(secret)" href="http://www.google.com">Google</a>`,
	)

	// Output:
	// <a href="http://www.google.com">Google</a>
	fmt.Println(html)
}
```

## XSS Code Pattern

### Tags / Elements

One of the following tags can generate JS execution:
* script
* style
* iframe
* object
* embed
* base

```regex
\w+\.AllowElements\((?:"(?:script|style|iframe|object|embed|base)"(?:,\s*"(?:script|style|iframe|object|embed|base)")*)?\)
```

