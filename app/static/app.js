// ServiceNow AI Demo — minimal JS

// Auto-dismiss flash messages after 5 seconds
document.addEventListener("DOMContentLoaded", () => {
  const flash = document.getElementById("flash-area");
  if (flash && !flash.classList.contains("hidden")) {
    setTimeout(() => {
      flash.style.transition = "opacity 0.5s";
      flash.style.opacity = "0";
      setTimeout(() => flash.remove(), 500);
    }, 5000);
  }
});
