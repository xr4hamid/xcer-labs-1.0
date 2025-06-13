// XCER Widget Bundle
(function () {
  console.log("✅ XCER Widget Loaded!");

  const iframe = document.createElement("iframe");
  
  iframe.src = "https://xcer-flask-backend.onrender.com/chat"; // ⚠️ Update this if port changes

  // ✅ Proper Chat Bubble Styling
  iframe.style.position = "fixed";
  iframe.style.bottom = "20px";
  iframe.style.right = "20px";
  iframe.style.width = "400px";
  iframe.style.height = "700px";
  iframe.style.border = "none";
  iframe.style.zIndex = "9999";
  iframe.style.borderRadius = "20px";
  iframe.style.boxShadow = "none";
  iframe.style.transition = "all 0.3s ease";
  iframe.style.overflow = "hidden";
iframe.style.backgroundColor = "transparent";

 // Or transparent if your React app handles it

  document.body.appendChild(iframe);
})();
