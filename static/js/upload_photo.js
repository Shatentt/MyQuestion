(function(){
    const fileInput = document.getElementById('avatarInput');
    const chooseBtn = document.getElementById('chooseBtn');
    const previewWrap = document.querySelector('.avatar-preview');
    const statusEl = document.getElementById('uploadStatus');
    
    const MAX_SIZE = 2 * 1024 * 1024;

    if (chooseBtn) {
        chooseBtn.addEventListener('click', () => fileInput.click());
    }

    if (previewWrap) {
        previewWrap.addEventListener('click', () => fileInput.click());
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files && e.target.files[0];
            statusEl.textContent = '';

            if (!file) return;

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
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'cover';
                
                previewWrap.innerHTML = '';
                previewWrap.appendChild(img);
            }
            
            img.src = objectUrl;

            img.onload = () => {
                URL.revokeObjectURL(objectUrl);
            };
        });
    }
})();