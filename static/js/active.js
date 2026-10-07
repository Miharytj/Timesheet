document.addEventListener("DOMContentLoaded", function () {
  // Récupérer l'URL actuelle de la page
  const currentPath = window.location.pathname;

  // Vérification plus stricte en utilisant startsWith
  if (currentPath.startsWith("/dashboard")) {
      document.getElementById("dashboard-link").classList.add("active");
  } else if (currentPath.startsWith("/timesheet")) {
      document.getElementById("timesheet-link").classList.add("active");
  } else if (currentPath.startsWith("/calendar")) {
      document.getElementById("calendar-link").classList.add("active");
  } else if (currentPath.startsWith("/people")) {
      document.getElementById("people-link").classList.add("active");
  } else if (currentPath.startsWith("/reports")) {
      document.getElementById("reports-link").classList.add("active");
  } else if (currentPath.startsWith("/parameter")) {
      document.getElementById("parameter-link").classList.add("active");
  }
});
