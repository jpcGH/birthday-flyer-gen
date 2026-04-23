(function () {
    const nameInput = document.getElementById('id_celebrant_name');
    const dateInput = document.getElementById('id_birthday_date');
    const wishInput = document.getElementById('id_wish');
    const photoInput = document.getElementById('id_uploaded_photo');
    const themeInput = document.getElementById('id_theme');

    const previewName = document.getElementById('previewName');
    const previewDate = document.getElementById('previewDate');
    const previewWish = document.getElementById('previewWish');
    const previewPhoto = document.getElementById('previewPhoto');
    const liveFlyer = document.getElementById('liveFlyer');

    if (!nameInput || !dateInput || !wishInput || !photoInput || !themeInput || !liveFlyer) {
        return;
    }

    const defaultWish = liveFlyer.dataset.defaultWish || '';

    function formatDate(dateValue) {
        if (!dateValue) {
            return 'Select birthday date';
        }
        const parsed = new Date(`${dateValue}T00:00:00`);
        if (Number.isNaN(parsed.getTime())) {
            return 'Select birthday date';
        }
        return parsed.toLocaleDateString('en-GB', {
            day: '2-digit',
            month: 'long',
            year: 'numeric',
        });
    }

    function updateTextPreview() {
        previewName.textContent = (nameInput.value || 'Celebrant Name').trim().toUpperCase();
        previewDate.textContent = formatDate(dateInput.value);
        previewWish.textContent = (wishInput.value || defaultWish).trim();
    }

    function updateTheme() {
        const themeClass = `theme-${themeInput.value.replace('_', '-')}`;
        liveFlyer.classList.remove('theme-royal-grace', 'theme-refuge-light', 'theme-covenant-bloom');
        liveFlyer.classList.add(themeClass);
    }

    function updateImagePreview() {
        const file = photoInput.files && photoInput.files[0];
        if (!file) {
            previewPhoto.src = 'https://placehold.co/410x410/png?text=Celebrant+Photo';
            return;
        }

        const reader = new FileReader();
        reader.onload = function (event) {
            previewPhoto.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }

    [nameInput, dateInput, wishInput].forEach((input) => {
        input.addEventListener('input', updateTextPreview);
    });

    dateInput.addEventListener('change', updateTextPreview);
    themeInput.addEventListener('change', updateTheme);
    photoInput.addEventListener('change', updateImagePreview);

    updateTextPreview();
    updateTheme();
})();
