document.addEventListener("DOMContentLoaded", async function () {
    var prevBtn = document.getElementById("prev");
    var nextBtn = document.getElementById("next");
    var todayBtn = document.getElementById("today");
    var titleSpan = document.getElementById("calendar-title");
    var employeeRows = document.getElementById("employee-rows");
  
    // Récupérer les employés depuis l'API
    let response = await fetch("/api/employes/");
    let employes = await response.json();
  
    // Ajouter les employés comme lignes dans le tableau
    employes.forEach((employe) => {
      let row = document.createElement("tr");
      let nameCell = document.createElement("td");
      nameCell.className = "employee-name";
      nameCell.textContent = employe.title; // Nom de l'employé
      row.appendChild(nameCell);
  
      // Ajouter des cellules vides pour chaque jour
      for (let i = 0; i < 7; i++) {
        let dayCell = document.createElement("td");
        row.appendChild(dayCell);
      }
  
      employeeRows.appendChild(row);
    });
  
    // Mettre à jour les dates de la table
    function updateTableDates(startDate) {
      let date = new Date(startDate);
      let today = new Date();
      for (let i = 1; i <= 7; i++) {
        let dayCell = document.getElementById(`day-${i}`);
        let cellDate = new Date(date);
        dayCell.textContent = cellDate.toLocaleDateString("fr-FR", {
          weekday: "short",
          day: "2-digit",
          month: "2-digit",
        });
  
        // Ajouter ou retirer la classe "active-day" pour le jour actuel
        if (cellDate.toDateString() === today.toDateString()) {
          dayCell.classList.add("active-day", "highlight-transition");
        } else {
          dayCell.classList.remove("active-day", "highlight-transition");
        }
  
        date.setDate(date.getDate() + 1);
      }
    }
  
    let currentStartDate = new Date();
    currentStartDate.setDate(
      currentStartDate.getDate() - currentStartDate.getDay()
    ); // Commence au dimanche
  
    function updateTitle() {
      titleSpan.textContent = `Semaine du ${currentStartDate.toLocaleDateString("fr-FR")}`;
    }
  
    // Navigation entre les semaines
    prevBtn.addEventListener("click", function () {
      currentStartDate.setDate(currentStartDate.getDate() - 7);
      updateTableDates(currentStartDate);
      updateTitle();
    });
  
    nextBtn.addEventListener("click", function () {
      currentStartDate.setDate(currentStartDate.getDate() + 7);
      updateTableDates(currentStartDate);
      updateTitle();
    });
  
    todayBtn.addEventListener("click", function () {
      currentStartDate = new Date();
      currentStartDate.setDate(
        currentStartDate.getDate() - currentStartDate.getDay()
      );
      updateTableDates(currentStartDate);
      updateTitle();
    });
  
    // Initialisation
    updateTableDates(currentStartDate);
    updateTitle();
  });
  