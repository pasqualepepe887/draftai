document.addEventListener('DOMContentLoaded', () => {
document.getElementById('file-input').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        console.log('Nome del file:', file.name);
        console.log('Dimensione del file (byte):', file.size);
        console.log('Tipo del file:', file.type);
        console.log('Ultima modifica:', file.lastModifiedDate);

        document.getElementById('div-scan').style.display = 'none';
        document.getElementById('div-img-upload').style.display = 'flex';
        document.getElementById('result').style.display = 'flex';
        document.getElementById('img_back').style.display = 'flex';
        
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.getElementById('img-upload');
            img.src = e.target.result;
            img.style.display = 'block'; 
        };
        const formData = new FormData();
        formData.append('file', file);
    
        // request POST
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Gestisci la risposta del server
            document.getElementById('title-idea-1').textContent = data.idea1_T;
            document.getElementById('title-idea-2').textContent = data.idea2_T;
            document.getElementById('title-idea-3').textContent = data.idea3_T;
            document.getElementById('img-1').src = data.idea1_I;
            document.getElementById('img-2').src = data.idea2_I;
            document.getElementById('img-3').src = data.idea3_I;
           
        })
        .catch(error => {
            console.error('Error:', error);
        });
        reader.readAsDataURL(file);
    }
  });
});
