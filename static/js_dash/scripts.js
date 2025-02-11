document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('nav ul li a');
    const sections = document.querySelectorAll('.tab-content');

    // GSAP pour l'animation d'apparition de la page
    gsap.to(".main-content", {
        duration: 1,
        opacity: 1,
        y: 0,
        ease: "power4.out"
    });

    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();

            // Masquer toutes les sections et supprimer l'onglet actif précédent
            sections.forEach(section => section.classList.remove('active'));
            tabs.forEach(t => t.classList.remove('active'));

            // Afficher la section correspondante et marquer l'onglet comme actif
            const targetId = tab.getAttribute('id').replace('-tab', '');
            const target = document.getElementById(targetId);
            target.classList.add('active');
            tab.classList.add('active');

            // Stocker l'onglet actif dans localStorage
            localStorage.setItem('activeTab', targetId);

            // GSAP pour l'animation de la section
            gsap.fromTo(target, {opacity: 0, y: 20}, {duration: 1, opacity: 1, y: 0, ease: "power4.out"});
        });
    });

    // Récupérer l'onglet actif depuis le localStorage
    const activeTab = localStorage.getItem('activeTab');

    if (activeTab) {
        // Afficher l'onglet stocké
        document.getElementById(`${activeTab}-tab`).click();
    } else {
        // Afficher la première section par défaut si rien n'est stocké
        tabs[0].click();
    }
});

// Gérer l'image de Modification
document.getElementById('fileInput').addEventListener('change', function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById('profilePic').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});
