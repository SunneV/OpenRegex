// static/js/utils/theme.js
import { applyDynamicStyles } from './regex.js';

const setThemeIcon = (themeSwitcher, isDarkTheme) => {
    // Sun icon for dark theme to switch to light, Moon icon for light theme to switch to dark
    themeSwitcher.innerHTML = isDarkTheme ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
};

export const toggleTheme = (body, themeSwitcher) => {
    const isDarkTheme = body.classList.contains('dark-theme');
    body.classList.toggle('dark-theme', !isDarkTheme);
    body.classList.toggle('light-theme', isDarkTheme);
    localStorage.setItem('theme', isDarkTheme ? 'light' : 'dark');
    setThemeIcon(themeSwitcher, !isDarkTheme);
};

export const applyTheme = (body, themeSwitcher) => {
    const savedTheme = localStorage.getItem('theme') === 'dark';
    body.classList.toggle('dark-theme', savedTheme);
    body.classList.toggle('light-theme', !savedTheme);
    setThemeIcon(themeSwitcher, savedTheme);
};