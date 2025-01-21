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