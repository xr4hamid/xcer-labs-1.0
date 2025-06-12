// public/widget-loader.js

(function () {
  const iframe = document.createElement("iframe");
  iframe.src = "https://your-domain.com/widget.html"; // ← isko bad me update karenge
  iframe.style.position = "fixed";
  iframe.style.bottom = "20px";
  iframe.style.right = "20px";
  iframe.style.width = "400px";
  iframe.style.height = "600px";
  iframe.style.border = "none";
  iframe.style.zIndex = "999999";
  iframe.style.borderRadius = "20px";
  iframe.style.boxShadow = "0 0 20px rgba(0,0,0,0.3)";
  document.body.appendChild(iframe);
})();
