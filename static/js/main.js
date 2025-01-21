// static/js/main.js

import { initThemeSwitcher } from './components/themeSwitcher.js';
import { initEngineSelector, initCheatSheetState } from './components/engineSelector.js';
import { initRegexInput, getRegexInputValue } from './components/regexInput.js';
import { initTextInput, getTextInputValue } from './components/textInput.js';
import { fetchRegexMatch } from './utils/regex.js';
import { matchesTable } from './components/output/matchesTable.js';
import { highlightText, highlightRegex } from './components/output/highlight.js';
import { execTime } from './components/output/executionTime.js';
import { webTime } from './components/output/webTime.js';
import { getElement } from './utils/dom.js';
import { attachMatchEventListeners } from './components/output/hoverHighlight.js';
import { initExampleButton, initClearButton } from './components/actionButton.js';

let timeoutId = null;


export const handleInputChange = async () => { // Add async here
    clearTimeout(timeoutId);
    const regex = getRegexInputValue();
    const text = getTextInputValue();
    const engine = getElement('engine-selector').value;
    const elements = { matchesTable, highlightText, highlightRegex, execTime, webTime };

    if (document.activeElement === getElement('engine-selector') || document.activeElement === getElement('theme-switcher')) {
        // Await the fetchRegexMatch function
        await fetchRegexMatch(regex, text, engine, elements);
    } else {
        timeoutId = setTimeout(async () => {
            // Await the fetchRegexMatch function inside the timeout as well
            await fetchRegexMatch(regex, text, engine, elements);
        }, 1000);
    }
};

document.addEventListener('DOMContentLoaded', async () => { // Add async here
    initThemeSwitcher();
    initEngineSelector();
    initCheatSheetState();
    initRegexInput();
    initTextInput();
    initExampleButton();
    initClearButton();
    const debugMode = getElement('mode');
     if (debugMode && debugMode.textContent.trim() !== "") {
        debugMode.style.display = 'block'; // Access style only if debugMode exists
    }

    const initialRegex = getRegexInputValue();
    const initialText = getTextInputValue();
    const initialEngine = getElement('engine-selector').value;
    const elements = { matchesTable, highlightText, highlightRegex, execTime, webTime };

    // Initial fetch on page load
    await fetchRegexMatch(initialRegex, initialText, initialEngine, elements);
    attachMatchEventListeners();
});