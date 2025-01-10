document.addEventListener('DOMContentLoaded', () => {
    const themeSwitcher = document.getElementById('theme-switcher');
    const body = document.body;
    const moonIcon = '<i class="fas fa-moon"></i>';
    const sunIcon = '<i class="fas fa-sun"></i>';
    const engineSelector = document.getElementById('engine-selector');
    const regexInput = document.getElementById('regex-input');
    const textInput = document.getElementById('text-input');
    const matchesOutput = document.getElementById('matches-table');
    const highlightOutput = document.getElementById('highlight');
    const engineVersionOutput = document.getElementById('selected-engine-version');
    const execTimeOutput = document.getElementById('exec-time');
    const webTimeOutput = document.getElementById('web-time');
    const dynamicStyles = document.getElementById('dynamic-styles');

    let darkThemeColors = {}; // Store dark theme colors
    let lightThemeColors = {}; // Store light theme colors
    let styleTextDark = '';
    let styleTextLight = '';
    let currentTheme = 'light-theme'; // default theme


    const applyDynamicStyles = () => {
        dynamicStyles.textContent =  currentTheme === 'dark-theme' ? styleTextDark : styleTextLight;
    }


    // Helper function to set theme
    const setTheme = (theme) => {
        body.classList.remove('light-theme', 'dark-theme');
        body.classList.add(theme);
        themeSwitcher.innerHTML = theme === 'dark-theme' ? sunIcon : moonIcon;
        localStorage.setItem('theme', theme);
        currentTheme = theme; // update current theme variable
        applyDynamicStyles();
    };


    // Initial theme setup
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme) {
        setTheme(storedTheme);
    }

    // Theme Switcher Event Listener
    themeSwitcher.addEventListener('click', () => {
        const newTheme = body.classList.contains('light-theme') ? 'dark-theme' : 'light-theme';
        setTheme(newTheme);
    });


    // Fetch engine info
    const loadEngineInfo = async (engine) => {
        try {
            const response = await fetch('/get_engine_info', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({engine})
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            engineVersionOutput.innerText = JSON.stringify(data.engine_version, null, 2).replace(/"/g, '');
            localStorage.setItem('selectedEngine', engine);
            engineSelector.value = engine;
        } catch (error) {
            console.error('Error fetching engine info:', error);
        }
    };

    // Initial engine setup
    const firstEngine = engineSelector.options[0].value;
    let selectedEngine = localStorage.getItem('selectedEngine') || firstEngine;
    loadEngineInfo(selectedEngine);

    // Engine Selector Event Listener
    engineSelector.addEventListener('change', () => {
        selectedEngine = engineSelector.value;
        loadEngineInfo(selectedEngine);
        handleInputChange();
    });


    // Regex Match Fetch
    const fetchRegexMatch = async (regex, text, engine) => {
        execTimeOutput.classList.add('loading');
        execTimeOutput.textContent = '';
        webTimeOutput.textContent = '';
        const startTime = performance.now();

        try {
            const isDarkTheme = currentTheme === 'dark-theme';
            const response = await fetch('/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({regex_input: regex, text_input: text, engine, is_dark_theme: isDarkTheme})
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            matchesOutput.innerHTML = data.matches_table;
            highlightOutput.innerHTML = data.highlighted_text;
            execTimeOutput.textContent = data.execution_time;
            // Capture Colors
            darkThemeColors = data.dark_theme_color;
            lightThemeColors = data.light_theme_color;


            // Generate and Store Style
             styleTextDark = generateDynamicStyles(darkThemeColors, true);
             styleTextLight = generateDynamicStyles(lightThemeColors, false);

             applyDynamicStyles();

        } catch (error) {
            console.error('Error fetching regex match', error)
        } finally {
            execTimeOutput.classList.remove('loading');
            const endTime = performance.now();
            const elapsedTime = endTime - startTime;
            webTimeOutput.textContent = `Web: ${Math.round(elapsedTime)} ms`;
        }
    };


    let timeoutId = null;

    // Input change handler
    const handleInputChange = () => {
        clearTimeout(timeoutId);

        const regex = regexInput.value;
        const text = textInput.value;
        const engine = engineSelector.value;

        if (document.activeElement === engineSelector || document.activeElement === themeSwitcher) {
            fetchRegexMatch(regex, text, engine);
        } else {
            timeoutId = setTimeout(() => fetchRegexMatch(regex, text, engine), 1500);
        }
    };

    // Event Listeners for input changes
    regexInput.addEventListener('input', handleInputChange);
    textInput.addEventListener('input', handleInputChange);

    // Initial fetchRegexMatch call
    const initialRegex = regexInput.value;
    const initialText = textInput.value;
    const initialEngine = selectedEngine;
    fetchRegexMatch(initialRegex, initialText, initialEngine);


    const generateDynamicStyles = (colors, isDarkTheme) => {
        let styleText = '';
        if (isDarkTheme) {
            for (const [key, color] of Object.entries(colors)) {
                styleText += `
                    .dark-theme .group-highlight.${key},
                    .dark-theme .group-table-highlight.${key} {
                        background-color: ${color};
                    }`;
            }
        } else {
            for (const [key, color] of Object.entries(colors)) {
                styleText += `
                    .light-theme .group-highlight.${key},
                    .light-theme .group-table-highlight.${key} {
                        background-color: ${color};
                    }`;
            }
        }

       return styleText;
    };


});