// Afficher les informations de la caissière dans un popup
function showCaissiereInfo() {
    document.getElementById("caissiereModal").style.display = "block";
}

// Afficher les informations du client dans un popup
function showClientInfo() {
    document.getElementById("clientModal").style.display = "block";
}

// Afficher la modale des produits
function showProductDetails() {
    document.getElementById("product-popup").style.display = "block"; // Affiche le popup
}

// Fermer les modales
function closeModal(modalId) {
    document.getElementById(modalId).style.display = "none";
}

// Ferme les modales lorsque l'utilisateur clique en dehors du contenu
window.onclick = function(event) {
    if (event.target === document.getElementById("product-popup")) {
        closeModal('product-popup');
    } else if (event.target === document.getElementById("caissiereModal")) {
        closeModal('caissiereModal');
    } else if (event.target === document.getElementById("clientModal")) {
        closeModal('clientModal');
    }
};

// Ferme le popup lorsque l'utilisateur clique sur le bouton de fermeture
document.getElementById("close-popup").addEventListener("click", function() {
    closeModal('product-popup');
});

document.addEventListener("DOMContentLoaded", () => {

    const userPic = document.getElementById("user-pic");
    userPic.addEventListener("click", toggleMenu);
    userPic.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
        toggleMenu();
    }
    });

    window.addEventListener("click", (event) => {
    const subMenu = document.getElementById("subMenu");
    if (!event.target.matches(".user-pic") && subMenu.classList.contains("open-menu")) {
        subMenu.classList.remove("open-menu");
    }
    });
});

function toggleMenu() {
const subMenu = document.getElementById("subMenu");
subMenu.classList.toggle("open-menu");
subMenu.setAttribute("aria-hidden", !subMenu.classList.contains("open-menu"));
}
