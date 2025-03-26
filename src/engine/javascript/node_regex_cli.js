// node_regex_cli.js
// Usage: node node_regex_cli.js <pattern> <text> <flags_string>
// Example: node node_regex_cli.js "a(b)c" "xx abc yy abc zz" "gi"

const patternStr = process.argv[2];
const text = process.argv[3];
const flagsStr = process.argv[4] || ''; // e.g., "gi" includes global and ignoreCase

let result = {
    matches: [],
    error: ""
};

try {
    // Ensure 'd' flag is included if supported and available for indices
    // Ensure 'g' flag is always included for finditer-like behavior
    let effectiveFlags = flagsStr;
    if (!effectiveFlags.includes('g')) {
        effectiveFlags += 'g';
    }
    // Add 'd' flag for indices if Node version supports it (v16.0.0+)
    // We'll try adding it; older versions might throw an error handled below.
    if (!effectiveFlags.includes('d')) {
        effectiveFlags += 'd';
    }

    let regex;
    try {
         regex = new RegExp(patternStr, effectiveFlags);
    } catch (e) {
        // If creating with 'd' flag failed, try without it (older Node versions)
        if (effectiveFlags.includes('d') && e instanceof SyntaxError) {
            effectiveFlags = effectiveFlags.replace('d', '');
            regex = new RegExp(patternStr, effectiveFlags);
        } else {
            throw e;
        }
    }


    let match;
    while ((match = regex.exec(text)) !== null) {
        // If the regex is empty (like //g), it might loop infinitely
        if (match[0].length === 0 && regex.lastIndex === match.index) {
            regex.lastIndex++;
        }

        const matchData = {
            match: match[0],
            index: [match.index, regex.lastIndex],
            groups: []
        };

        // Check if indices ('d' flag) are available
        const hasIndices = match.indices !== undefined && match.indices !== null;

        // Process groups (skip the full match at index 0)
        for (let i = 1; i < match.length; i++) {
            const groupValue = match[i];
            let groupIndex = [];
            let groupName = ""; // JavaScript doesn't easily expose numbered group names

            if (groupValue !== undefined) {
                 if (hasIndices && match.indices[i]) {
                    groupIndex = [match.indices[i][0], match.indices[i][1]];
                 } else {
                    groupIndex = [];
                 }
            } else {
                 groupIndex = [];
            }

             // Handle named groups
             if (match.groups) {
                for (const name in match.groups) {
                    // Find which numbered group corresponds to this named group
                    // This relies on the assumption that named groups also appear in the numbered match array
                    if (match.groups[name] === groupValue) {
                         // Heuristic: If we find a match by value, assume it's the correct name.
                         // This isn't perfect if multiple groups capture the same value.
                         // A more robust approach might require parsing the pattern, which is complex.
                         // Check if the index matches as well if available
                         if (hasIndices && match.indices.groups && match.indices.groups[name] && match.indices.groups[name][0] === groupIndex[0]) {
                            groupName = name;
                            break; // Found the name for this group index
                         } else if (!hasIndices) {
                            // Without indices, rely solely on value match
                            groupName = name;
                            // Don't break immediately, another named group might have the same value
                         }
                    }
                }
            }

            matchData.groups.push({
                name: groupName,
                // Ensure null/undefined becomes empty string to match Python structure
                value: groupValue === undefined || groupValue === null ? "" : groupValue,
                index: groupIndex
            });
        }
         // Add named groups that might not have been matched if not captured by value check
         if (hasIndices && match.indices.groups) {
            for (const name in match.indices.groups) {
                let found = matchData.groups.some(g => g.name === name);
                if (!found) {
                     const namedGroupValue = match.groups[name];
                     const namedGroupIndex = match.indices.groups[name] ? [match.indices.groups[name][0], match.indices.groups[name][1]] : [];
                     matchData.groups.push({
                        name: name,
                        value: namedGroupValue === undefined || namedGroupValue === null ? "" : namedGroupValue,
                        index: namedGroupIndex,
                    });
                }
            }
        }


        result.matches.push(matchData);
    }

} catch (e) {
    result.error = e.message || String(e);
}

console.log(JSON.stringify(result));