(function(){
    const fileInput = document.getElementById('avatarInput');
    const chooseBtn = document.getElementById('chooseBtn');
    const previewWrap = document.querySelector('.avatar-preview');
    const statusEl = document.getElementById('uploadStatus');
    const submitBtn = document.querySelector('.submit_btn');

    const MAX_SIZE = 2 * 1024 * 1024;

    chooseBtn.addEventListener('click', () => fileInput.click());

    previewWrap.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files && e.target.files[0];
        statusEl.textContent = '';

        if (!file) {
        return;
        }

        if (!file.type.startsWith('image/')) {
        statusEl.textContent = 'Пожалуйста, выберите изображение.';
        fileInput.value = '';
        return;
        }

        if (file.size > MAX_SIZE) {
        statusEl.textContent = 'Файл слишком большой (макс 2 MB).';
        fileInput.value = '';
        return;
        }

        const objectUrl = URL.createObjectURL(file);

        let img = previewWrap.querySelector('img');
        if (!img) {
        img = document.createElement('img');
        previewWrap.innerHTML = '';
        previewWrap.appendChild(img);
        }
        img.src = objectUrl;

        img.onload = () => {
        URL.revokeObjectURL(objectUrl);
        };

        if (submitBtn) {
        submitBtn.disabled = false;
        }
    });

    const form = document.querySelector('.question_form');
    if (form) {
        form.addEventListener('submit', () => {
        
        });
    }
})();