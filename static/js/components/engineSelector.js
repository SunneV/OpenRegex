// static/js/components/engineSelector.js

import { getElement } from '../utils/dom.js';
import { handleInputChange } from '../main.js';

const engineSelector = getElement('engine-selector');
const engineVersionOutput = getElement('selected-engine-version');

const engineCheatSheetOutput = getElement('regex-cheat-sheet');
const cheatSheetWrapper = getElement('cheat-sheet-wrapper');
const toggleCheatSheetButton = getElement('toggle-cheat-sheet');

// Function to toggle the cheat sheet visibility
const toggleCheatSheet = () => {
    const isCollapsed = engineCheatSheetOutput.classList.contains('collapsed');

    if (isCollapsed) {
        engineCheatSheetOutput.classList.remove('collapsed');
        cheatSheetWrapper.style.display = 'flex';
        toggleCheatSheetButton.textContent = 'Hide Cheat Sheet';
        localStorage.setItem('cheatSheetState', 'visible');

    } else {
        engineCheatSheetOutput.classList.add('collapsed');
        cheatSheetWrapper.style.display = 'none';
        toggleCheatSheetButton.textContent = 'Show Cheat Sheet';
        localStorage.setItem('cheatSheetState', 'collapsed');
    }
};




toggleCheatSheetButton.addEventListener('click', toggleCheatSheet);

const loadEngineInfo = async (engine) => {
    try {
        const response = await fetch('/get_engine_info', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ engine })
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        engineVersionOutput.innerText = JSON.stringify(data.engine_version, null, 2).replace(/"/g, '');
        createCheatSheetTables(data.cheat_sheet);
        localStorage.setItem('selectedEngine', engine);
        engineSelector.value = engine;
    } catch (error) {
        console.error('Error fetching engine info:', error);
    }
};

const createCheatSheetTables = (cheatSheetData) => {
    const leftOutput = document.getElementById('regex-cheat-sheet-left');
    const rightOutput = document.getElementById('regex-cheat-sheet-right');
    leftOutput.innerHTML = ''; // Clear existing content
    rightOutput.innerHTML = ''; // Clear existing content

    let leftHeight = 0;
    let rightHeight = 0;
    let firstElementHeight = 0;

    for (let i = 0; i < cheatSheetData.length; i++) {
        const categoryData = cheatSheetData[i];
        const categoryName = categoryData.category;
        const items = categoryData.items;

        // Create container for category (h3 + table)
        const categoryContainer = document.createElement('div');
        categoryContainer.classList.add('category-item');

        // Create h3 element for category title
        const categoryTitle = document.createElement('h3');
        categoryTitle.textContent = categoryName;
        categoryContainer.appendChild(categoryTitle);

        const table = document.createElement('table');
        const tbody = document.createElement('tbody');

        // Create table rows
        for (const item of items) {
            const row = document.createElement('tr');
            const charCell = document.createElement('td');
            const descCell = document.createElement('td');
            charCell.textContent = item.character;
            descCell.textContent = item.description;
            row.appendChild(charCell);
            row.appendChild(descCell);
            tbody.appendChild(row);
        }

        table.appendChild(tbody);
        categoryContainer.appendChild(table);

        // Calculate the height of the category container (including h3)
        const categoryContainerHeight = categoryContainer.offsetHeight + categoryTitle.offsetHeight;

        // Determine which side to add the element to
        let side = 'left'; // Default to left

        if (i === 0) {
            side = 'left';
            firstElementHeight = categoryContainerHeight; // Include h3 height
        } else if (i === 1) {
            side = 'right';
        } else if (i > 1 && rightHeight + categoryContainerHeight > leftHeight && leftHeight + categoryContainerHeight <= firstElementHeight * 1.3) {
            side = 'left';
        } else if (i > 1 && rightHeight + categoryContainerHeight <= leftHeight) {
            side = 'right';
        } else {
            side = 'left';
        }

        // Append to the correct output container based on the side
        if (side === 'left') {
            leftOutput.appendChild(categoryContainer);
            leftHeight += categoryContainerHeight; // Add h3 height as well
        } else {
            rightOutput.appendChild(categoryContainer);
            rightHeight += categoryContainerHeight; // Add h3 height as well
        }
    }
};

export const initEngineSelector = () => {
    const firstEngine = engineSelector.options[0].value;
    let selectedEngine = localStorage.getItem('selectedEngine') || firstEngine;
    loadEngineInfo(selectedEngine);

    engineSelector.addEventListener('change', () => {
        loadEngineInfo(engineSelector.value);
        handleInputChange();
    });
};
export const initCheatSheetState = () => {
    // Hide by default
    engineCheatSheetOutput.classList.add('collapsed');
    cheatSheetWrapper.style.display = 'none';
    toggleCheatSheetButton.textContent = 'Show Cheat Sheet';

    // Check local storage for previous state
    const storedState = localStorage.getItem('cheatSheetState');
    if (storedState === 'visible') {
        // If it was previously visible, show it
        engineCheatSheetOutput.classList.remove('collapsed');
        cheatSheetWrapper.style.display = 'flex';
        toggleCheatSheetButton.textContent = 'Hide Cheat Sheet';
        createCheatSheetTables(cheatSheetData);
    }
};