document.addEventListener('DOMContentLoaded', function() {
    const showFormBtn = document.getElementById('showFormBtn');
    const tabletForm = document.getElementById('tabletForm');
    const tabletTable = document.getElementById('tabletTable').getElementsByTagName('tbody')[0];
    const purchasesPopup = document.getElementById('purchasesDetailsPopup');
    const closePopupBtn = document.querySelector('.close');

    let isEditing = false;
    let currentRow;

    // Afficher/cacher le formulaire
    showFormBtn.addEventListener('click', () => {
        tabletForm.classList.toggle('hidden');
        if (!tabletForm.classList.contains('hidden')) {
            tabletForm.reset();
            document.querySelector('button[type="submit"]').textContent = 'Ajouter';
            isEditing = false;
            currentRow = null;
        }
    });

    // Créer une nouvelle ligne dans le tableau
    function createTableRow(username, id, password, status) {
        const newRow = tabletTable.insertRow();
        newRow.innerHTML = `
            <td>${username}</td>
            <td>${id}</td>
            <td>${password}</td>
            <td>${status === 'connected' ? 'Connecté' : 'Déconnecté'}</td>
            <td>
                <button class="disconnect-btn">Déconnecter</button>
                <button class="edit-btn">Modifier</button>
                <button class="delete-btn">Supprimer</button>
            </td>
            <td>
                <button class="view-btn"><span class="material-symbols-outlined">visibility</span></button>
            </td>
        `;



        newRow.querySelector('.disconnect-btn').addEventListener('click', () => {
            newRow.cells[3].textContent = 'Déconnecté';
            newRow.classList.remove('connected');
            newRow.classList.add('disconnected');
        });

        newRow.querySelector('.edit-btn').addEventListener('click', () => {
            isEditing = true;
            currentRow = newRow;
            document.getElementById('username').value = newRow.cells[0].textContent;
            document.getElementById('id').value = newRow.cells[1].textContent;
            document.getElementById('password').value = newRow.cells[2].textContent;
            document.getElementById('status').value = newRow.cells[3].textContent === 'Connecté' ? 'connected' : 'disconnected';
            tabletForm.classList.remove('hidden');
            showFormBtn.classList.add('hidden');
            document.querySelector('button[type="submit"]').textContent = 'Valider';
        });

        // newRow.querySelector('.delete-btn').addEventListener('click', () => {
        //     newRow.remove();
        //     if (tabletTable.rows.length === 0) {
        //         tabletForm.classList.remove('hidden');
        //         showFormBtn.classList.remove('hidden');
        //     }
        // });
    }

    // Gestionnaire pour le bouton de fermeture de la popup
    closePopupBtn.addEventListener('click', () => {
        purchasesPopup.classList.add('hidden');
    });

    // Gestionnaire pour la soumission du formulaire
    tabletForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const id = document.getElementById('id').value;
        const password = document.getElementById('password').value;
        const status = document.getElementById('status').value;

        if (isEditing && currentRow) {
            currentRow.cells[0].textContent = username;
            currentRow.cells[1].textContent = id;
            currentRow.cells[2].textContent = password;
            currentRow.cells[3].textContent = status === 'connected' ? 'Connecté' : 'Déconnecté';
            currentRow.classList.remove('connected', 'disconnected');
            currentRow.classList.add(status === 'connected' ? 'connected' : 'disconnected');

            isEditing = false;
            currentRow = null;
            document.querySelector('button[type="submit"]').textContent = 'Ajouter';
        } else {
            createTableRow(username, id, password, status);
        }

        tabletForm.reset();
        tabletForm.classList.add('hidden');
        showFormBtn.classList.remove('hidden');
    });
});
