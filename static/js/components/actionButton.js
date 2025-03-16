// static/js/components/exampleButton.js
import { getElement } from '../utils/dom.js';
import { handleInputChange } from '../main.js';

export const initExampleButton = () => {
    const exampleButton = getElement('fill-example');
    const engineSelect = getElement('engine-selector');

    exampleButton.addEventListener('click', async () => {
        const selectedEngine = engineSelect.value;

        try {
            const response = await fetch('/get_example_regex', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ engine: selectedEngine })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.error) {
                console.error(data.error);
            } else {
                document.getElementById('regex-input').value = data.input_regex;
                document.getElementById('text-input').value = data.input_text;
                handleInputChange();
            }
        } catch (error) {
            console.error('Error fetching example regex:', error);
        }
    });
};

export const initClearButton = () => {
    const clearButton = getElement('clear-input');
    const regexInput = getElement('regex-input');
    const textInput = getElement('text-input');

    clearButton.addEventListener('click', () => {
        regexInput.value = '';
        textInput.value = '';
        handleInputChange();
    });
};

export const initGenerateLinkButton = () => {
    const generateLinkButton = getElement('generate-link');

    generateLinkButton.addEventListener('click', () => {
       const urlParams = new URLSearchParams(window.location.search);
        const base64Encoded = urlParams.get('link');

        const currentUrl = window.location.origin;

        const generatedLink = `${currentUrl}/?link=${base64Encoded}`;

        if (generatedLink.length > 2000) {
            displayWarningMessage('The generated link is too long for the web!');
        } else {
            navigator.clipboard.writeText(generatedLink).then(() => {
                // Display a balloon message to confirm the link was copied
                showBalloonMessage('Link copied to clipboard!');
            }).catch((err) => {
                console.error('Failed to copy the link:', err);
            });
        }
    });
};

const showBalloonMessage = (message) => {
    const balloon = document.createElement('div');
    balloon.textContent = message;
    balloon.style.position = 'fixed';
    balloon.style.bottom = '20px';
    balloon.style.right = '20px';
    balloon.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    balloon.style.color = 'white';
    balloon.style.padding = '10px 20px';
    balloon.style.borderRadius = '8px';
    balloon.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.2)';
    balloon.style.zIndex = '1000';
    balloon.style.transition = 'opacity 0.5s ease';

    document.body.appendChild(balloon);

    // Automatically hide the message after 3 seconds
    setTimeout(() => {
        balloon.style.opacity = '0';
        setTimeout(() => document.body.removeChild(balloon), 500);
    }, 3000);
};

const displayWarningMessage = (message) => {
    const warning = document.createElement('div');
    warning.textContent = message;
    warning.style.position = 'fixed';
    warning.style.bottom = '20px';
    warning.style.right = '20px';
    warning.style.backgroundColor = 'red';
    warning.style.color = 'white';
    warning.style.padding = '10px 20px';
    warning.style.borderRadius = '8px';
    warning.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.2)';
    warning.style.zIndex = '1000';
    warning.style.transition = 'opacity 0.5s ease';

    document.body.appendChild(warning);

    // Automatically hide the warning message after 5 seconds
    setTimeout(() => {
        warning.style.opacity = '0';
        setTimeout(() => document.body.removeChild(warning), 500);
    }, 5000);
};