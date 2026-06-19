const addButton = document.querySelector("#add-subject");
const container = document.querySelector("#subjects-container");

addButton.addEventListener("click", function () {
  
  const input = document.createElement("input");
  input.type = "text";
  input.name = "subjects";
  input.placeholder = "Add the subject name";

  container.appendChild(input);
});

const searchInput = document.querySelector("#search-input");
const cards = document.querySelectorAll(".tutor-card");
searchInput.addEventListener("input", function () {

  const searchText = searchInput.value.toLowerCase().trim();
  let filteredTutors = 0;
  for (const card of cards) {
    const cardText = card.querySelector(".tutor-name").textContent.toLowerCase();
    if (cardText.includes(searchText)) {
      card.classList.remove("hidden-card");
    } else {
      card.classList.add("hidden-card");
    }
  }
});

