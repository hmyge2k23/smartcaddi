let subMenu = document.getElementById("subMenu");

function toggleMenu() {
    subMenu.classList.toggle("open-menu");
}

// Fermer le sous-menu quand on clique en dehors
window.onclick = function(event) {
    // Vérifie si le clic est à l'extérieur du subMenu et de l'image de profil
    if (!subMenu.contains(event.target) && !event.target.closest('.user-pic')) {
        subMenu.classList.remove("open-menu");
    }
} 