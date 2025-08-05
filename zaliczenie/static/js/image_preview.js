document.getElementById('id_image').addEventListener('change', function(event){
    const [file] = this.files;
    if (file){
        const preview = document.getElementById('image_preview');
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
    }
})