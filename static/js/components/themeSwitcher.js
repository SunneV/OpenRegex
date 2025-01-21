// static/js/components/themeSwitcher.js

import { toggleTheme, applyTheme } from '../utils/theme.js';
import { getElement } from '../utils/dom.js';
import { applyDynamicStyles, generateDynamicStyles } from '../utils/regex.js'; // Import necessary functions

const themeSwitcher = getElement('theme-switcher');
const body = document.body;

export const initThemeSwitcher = () => {
    let dark = localStorage.getItem('darkThemeColors');
    let light = localStorage.getItem('lightThemeColors');

    applyTheme(body, themeSwitcher); // Apply theme on initialization

    themeSwitcher.addEventListener('click', () => {
        toggleTheme(body, themeSwitcher);

        // Get the updated theme colors after toggling
        const darkThemeColors = JSON.parse(localStorage.getItem('darkThemeColors')) || {};
        const lightThemeColors = JSON.parse(localStorage.getItem('lightThemeColors')) || {};

        // Update dynamic styles after theme change
        applyDynamicStyles(darkThemeColors, lightThemeColors);
    });
};