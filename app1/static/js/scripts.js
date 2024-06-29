// scripts.js
document.getElementById('action-button').addEventListener('click', function() {
    let inputText = document.getElementById('text-input').value;
    if (inputText.trim() === '') {
        alert('请输入一些文本。');
        return;
    }

    this.disabled = true;
    let outputDiv = document.getElementById('text-output');
    outputDiv.innerHTML += `<p>User: ${inputText}</p>`;

    fetch('/api/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputText }),
    })
    .then(response => response.json())
    .then(data => {
        outputDiv.innerHTML += `<p>Jarvis: ${data.response}</p>`;
        document.getElementById('text-input').value = '';
        this.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        this.disabled = false;
    });
});

document.getElementById('normal-mode').addEventListener('click', function() {
    // Implement normal mode logic here
    console.log('Normal mode selected');
});

document.getElementById('multimodal-mode').addEventListener('click', function() {
    // Implement multimodal mode logic here
    console.log('Multimodal mode selected');
});

document.getElementById('motion-mode').addEventListener('click', function() {
    // Implement motion mode logic here
    console.log('Motion mode selected');
});
