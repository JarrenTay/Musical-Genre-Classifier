var url_string = "http://www.example.com/t.html?a=1&b=3&c=m2-m3-m4-m5"; //window.location.href
var url = new URL(url_string);
var code = url.searchParams.get("code");

var codeSpan = document.createElement("span");
codeSpan.id = "codeSpan";

var codeSpanContent = document.createTextNode(code);
codeSpan.appendChild(codeSpanContent);

var phSpan = document.getElementById('placeholder');
var parentDiv = phSpan.parentNode;

parentDiv.replaceChild(codeSpan, phSpan);

