document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('upload-form');
    const loading = document.getElementById('loading');
    const resultContainer = document.getElementById('result-container');
    const imagePreview = document.getElementById('image-preview');
    const answerDiv = document.getElementById('answer');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const imageFile = document.getElementById('image-upload').files[0];
        const question = document.getElementById('question').value;
        
        if (!imageFile || !question) return;
        
        // Show loading
        loading.style.display = 'block';
        resultContainer.style.display = 'none';
        
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('question', question);
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('Network response was not ok');
            
            const data = await response.json();
            
            // Display results
            imagePreview.innerHTML = `<img src="${data.image}" alt="Uploaded image">`;
            answerDiv.textContent = data.answer;
            
            // Show results
            loading.style.display = 'none';
            resultContainer.style.display = 'flex';
        } catch (error) {
            console.error('Error:', error);
            loading.textContent = 'Error processing your request. Please try again.';
            setTimeout(() => {
                loading.style.display = 'none';
                loading.textContent = 'Processing...';
            }, 3000);
        }
    });
});
