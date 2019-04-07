var url = window.location.href;
console.log(url)
var urlList = url.split('?code=');
var code = urlList[1];
console.log(code);
var codeSpan = document.createElement("span");
codeSpan.id = "codeSpan";

var codeSpanContent = document.createTextNode(code);
codeSpan.appendChild(codeSpanContent);

var phSpan = document.getElementById('placeholder');
var parentDiv = phSpan.parentNode;

parentDiv.replaceChild(codeSpan, phSpan);

