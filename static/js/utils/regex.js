// static/js/utils/regex.js

import { attachMatchEventListeners } from '../components/output/hoverHighlight.js';

export const fetchRegexMatch = async (regex, text, engine, elements) => {
    const { matchesTable, highlightText, highlightRegex, execTime, webTime } = elements;

    execTime.classList.add('loading');
    execTime.textContent = '';
    webTime.textContent = '';
    const startTime = performance.now();

    try {
        const response = await fetch('/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ regex_input: regex, text_input: text, engine }) // Now send isDarkTheme
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        matchesTable.innerHTML = data.matches_table;
        highlightText.innerHTML = data.highlighted_text;
        highlightRegex.innerHTML = data.highlighted_regex;
        execTime.textContent = data.execution_time;

        // Store the fetched colors in localStorage
        localStorage.setItem('darkThemeColors', JSON.stringify(data.dark_theme_color));
        localStorage.setItem('lightThemeColors', JSON.stringify(data.light_theme_color));

        // Apply dynamic styles based on the fetched colors
        applyDynamicStyles(data.dark_theme_color, data.light_theme_color);

        attachMatchEventListeners();

        if (data.encode_data) {
            const newUrl = `${window.location.origin}${window.location.pathname}?link=${data.encode_data}`;
            window.history.replaceState({}, document.title, newUrl);
        }
    } catch (error) {
        console.error('Error fetching regex match', error);
    } finally {
        execTime.classList.remove('loading');
        const endTime = performance.now();
        const elapsedTime = endTime - startTime;
        webTime.textContent = `Web: ${Math.round(elapsedTime)} ms`;
    }
};


export const generateDynamicStyles = (colors, isDarkTheme) => {
    let styleText = '';
    if (isDarkTheme) {
        for (const [key, color] of Object.entries(colors)) {
            styleText += `
                .dark-theme .regex-highlight.${key},
                .dark-theme .group-highlight.${key},
                .dark-theme .group-table-highlight.${key} {
                    background-color: ${color};
                }`;
        }
    } else {
        for (const [key, color] of Object.entries(colors)) {
            styleText += `
                .light-theme .regex-highlight.${key},
                .light-theme .group-highlight.${key},
                .light-theme .group-table-highlight.${key} {
                    background-color: ${color};
                }`;
        }
    }

   return styleText;
};

export const applyDynamicStyles = (darkThemeColors, lightThemeColors) => {
    const dynamicStyles = document.getElementById('dynamic-styles');
    const body = document.body;
    const isDarkTheme = body.classList.contains('dark-theme');
    const styleText = generateDynamicStyles(isDarkTheme ? darkThemeColors : lightThemeColors, isDarkTheme);
    dynamicStyles.textContent = styleText;
};

export const fetchAndDecodeLink = async (encodedData) => {
    try {
        const response = await fetch('/get_decode_link', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ encoded_data: encodedData })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json(); // Return the decoded data
    } catch (error) {
        console.error('Error fetching or decoding link data:', error);
        return null; // Return null on error
    }
};